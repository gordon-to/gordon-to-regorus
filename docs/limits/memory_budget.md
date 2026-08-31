# RVM memory budgets

RVM run-to-completion evaluation supports an optional memory budget when Regorus is built with the `allocator-memory-limits` feature.

The budget limits additional live bytes on the execution thread. Regorus captures a baseline when execution starts and compares later live-byte samples with that baseline. Each Rust `execute`, `execute_entry_point_by_name`, or `execute_entry_point_by_index` call starts with a fresh execution-only budget.

```rust
use core::num::NonZeroU64;
use regorus::rvm::vm::RegoVM;
use regorus::MemoryBudgetConfig;

let mut vm = RegoVM::new();
vm.set_memory_budget_config(Some(MemoryBudgetConfig {
    limit: NonZeroU64::new(16 * 1024 * 1024).expect("non-zero budget"),
}));
```

No configured budget preserves existing RVM behavior. A zero-byte budget is not representable in Rust and is rejected by language bindings.

## Included work

The `execute*` APIs start their budget when RVM execution begins. Fresh execution-state initialization, rule evaluation, and allocations retained by the result count against the budget.

Program compilation, program loading, data loading, input loading, and context loading happen before and outside the execution baseline and are not charged.

The C FFI keeps an internal execution window open through immediate native result JSON serialization and `CString` allocation, then closes it on success, error, or unwinding. The C# binding receives that native string after the window has closed, so managed UTF-8 decoding and managed `string` allocation are excluded.

There is no public multi-call begin/end memory-budget scope. Public scopes could be abandoned or move across threads while allocator counters are thread-local. Rust, C FFI, and C# are supported by this API; other bindings require follow-up work.

## Enforcement

Regorus samples memory at VM instruction checkpoints and once before returning a successful result. The C FFI also samples after native result JSON serialization and `CString` allocation. Enforcement is cooperative and checkpoint-based, not an allocation-time peak-memory hard cap. One instruction, builtin, result serialization, or `CString` allocation can temporarily overshoot the configured limit before the next sample. For example, a builtin can allocate far more than its remaining headroom and be rejected only after it returns; an allocation created and freed entirely between samples may not be observed at all. Callers should configure enough headroom for this overshoot.

Accounting uses the execution thread's live-byte counter rather than allocation ownership. Allocations and frees performed by synchronous host callbacks or builtins on that thread affect the observation. Objects allocated on one thread and freed on another can temporarily skew thread-level observations while allocator counters are reconciled. The control therefore bounds observed additional live bytes on the execution thread, not memory owned by a query or attributed across threads.

When a sampled live-byte count falls below the current baseline, Regorus lowers the baseline so an observed same-thread free does not grant headroom to later allocations. This downward ratchet is never restored during the execution and can make the effective budget stricter than configured after unrelated or legitimate frees. A foreign free can still offset evaluation allocations when both occur between samples.

A fresh budget means a new baseline is captured for each execution, not that the VM is returned to a newly constructed state. Reused VMs retain capacities and pools that are already live before the baseline. An identical policy and input can therefore allocate differently, and may have a different budget outcome, on a warm VM than on a fresh VM.

Exhaustion returns `VmError::MemoryBudgetExceeded`, including:

- `usage`, the observed execution-thread live-byte increase above the ratcheted baseline; this is diagnostic thread-level change, not exact query-owned memory
- configured budget
- VM program counter

The VM transitions to `ExecutionState::Error` and releases values retained by a failed execution. The C FFI reports `RegorusStatus::MemoryBudgetExceeded`, including when native result serialization or `CString` allocation exceeds the budget. The C# binding throws `RegorusMemoryBudgetExceededException`. Every terminal path clears its execution window, and reused VMs get a fresh budget for the next execution.

## Execution modes

The first implementation supports run-to-completion execution only. Configuring a budget and starting or resuming suspendable execution returns `VmError::MemoryBudgetUnsupportedInSuspendableExecution`. The FFI reports `RegorusStatus::MemoryBudgetUnsupportedInSuspendableExecution`, and C# throws `RegorusMemoryBudgetUnsupportedException`.

Suspendable execution may resume on another thread. A thread-local baseline cannot safely span that migration without evaluation-owned allocation attribution.

## Process-global limit

The existing process-global memory limit remains separate. It protects the process as a whole and is not an isolation mechanism for individual evaluations. When both controls are configured, the per-evaluation budget is checked first.
