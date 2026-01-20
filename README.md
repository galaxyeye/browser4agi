# browser4agi：A Self-Evolving Browser Agent Architecture

## 摘要（Abstract）

browser4agi 是一个面向 **“完全自主上网”** 目标而设计的自进化浏览器智能体系统。与传统基于 Prompt 或固定 Workflow 的 Agent 不同，browser4agi 将“浏览行为”视为一个 **可执行、可反思、可演化、可约束的控制系统**。

系统以规则驱动的 Tool DAG 为核心执行模型，通过 **失败驱动的反思（Reflection）**、**A/B Simulation 验证**、**受预算约束的 Patch 选择**，以及 **版本化 WorldModel**，实现了在无人工干预下持续提升成功率、同时避免规则爆炸的能力。

本文完整阐述 browser4agi 的架构设计、核心数据结构、演化闭环与工程约束，并讨论其在 Web Automation、Agent Research 以及通用 Self-Evolving System 中的意义。

---

## 1. 问题背景

### 1.1 为什么“自主上网”是一个困难问题

真实世界的网站具有以下特征：

* 页面结构高度异构且持续变化
* 强依赖动态 DOM、异步加载、登录态
* 操作存在隐含顺序与前置条件
* 局部规则往往只在单一站点或短时间内有效

这使得：

* **静态爬虫规则不可维护**
* **端到端 LLM Agent 成本高、不可解释、不稳定**

### 1.2 现有 Agent 架构的局限

主流 Agent 框架通常：

* 将 LLM 置于决策核心
* 缺乏长期记忆与规则演化机制
* 无法解释“为什么失败 / 为什么成功”
* 难以控制规模增长（Rule Explosion）

browser4agi 的设计目标正是解决这些根本性问题。

---

## 2. 核心设计理念

browser4agi 的架构基于四个核心原则：

1. **Execution First**：一切从可执行的 Tool DAG 开始
2. **Failure Driven Learning**：只有失败才触发学习
3. **Simulation Before Mutation**：任何修改必须先通过模拟验证
4. **Global Constraint Over Local Optimal**：演化必须受全局预算与 Pareto 最优约束

这使系统更接近一个 **工程化的控制系统**，而非纯生成式 Agent。

---

## 3. 系统总体架构

```
WorldModel (Versioned Rules)
        ↓
DagBuilder (Rule-driven)
        ↓
Tool DAG Execution
        ↓
ExecutionReport + BuildTrace
        ↓
DAG Reflection (v1 / v2)
        ↓
PatchProposal
        ↓
A/B Simulation
        ↓
Rule Explosion Control (Budget + Pareto)
        ↓
PatchApplier
        ↓
WorldModel++
```

这一闭环构成了 browser4agi 的 **自进化主循环**。

---

## 4. WorldModel：可版本化的世界认知

### 4.1 定义

WorldModel 是系统对“如何在网页中行动”的全部知识集合，其核心是 **规则（Rule）**。

每一次 WorldModel 的变更都会生成一个新的不可变快照：

```kotlin
data class WorldModelSnapshot(
    val version: String,
    val parentVersion: String?,
    val rules: List<Rule>
)
```

### 4.2 版本 DAG

* WorldModel 的演化形成一张有向无环图（DAG）
* 支持分支、回滚、A/B 并行实验
* 每一次 Patch 都是可审计、可复现的

---

## 5. 执行模型：Rule-driven Tool DAG

### 5.1 为什么是 DAG

* 浏览行为天然具有依赖关系（登录 → 跳转 → 操作）
* DAG 能显式表达顺序、前置条件与并行性

### 5.2 DagBuilder

DagBuilder 根据当前 WorldModel 与任务目标，选择满足条件的规则构建 Tool DAG，并记录 **BuildTrace**：

```kotlin
data class BuildTrace(
    val nodeId: String,
    val appliedRuleId: String,
    val reason: String
)
```

BuildTrace 是后续 Reflection 的“证据链”。

---

## 6. 失败反思：DAG Reflection

### 6.1 Reflection v1（规则版）

* 仅基于 ExecutionReport + BuildTrace
* 识别责任规则（blame assignment）
* 生成最小 Patch（narrow / add precondition / add order constraint）

### 6.2 Reflection v2（LLM 辅助）

* LLM 仅作为“顾问”生成 PatchCandidate
* 严格受限于结构化 Schema 与白名单操作
* 不允许直接修改 WorldModel

---

## 7. Simulation：在修改前验证

### 7.1 A/B Simulation

* 在相同任务集上并行执行：

    * Baseline WorldModel
    * Patched WorldModel

### 7.2 WorldModelDiff

Simulation 的结果以 WorldModelDiff + Metrics 表达：

* 成功率变化
* 稳定性变化
* 规则复杂度变化

---

## 8. Rule Explosion Control v2

### 8.1 全局 Patch Budget

系统在固定时间窗内仅允许有限 Patch 被接受：

* 最大 Patch 数
* 最大规则增量

### 8.2 Pareto Frontier

Patch 被视为多目标优化问题：

* maximize successDelta
* minimize ruleCountDelta
* minimize specializationScore

只有位于 Pareto Front 且满足预算的 Patch 才可能被应用。

---

## 9. PatchApplier：唯一写入口

PatchApplier 是系统中 **唯一允许修改 WorldModel 的组件**：

* 强制所有修改经过 Simulation + 控制器
* 写入版本化 Repo
* 记录 Patch 与 Experiment 的完整谱系

---

## 10. 规则生命周期管理

通过 RuleStatsUpdater：

* 规则会随时间衰减置信度
* 自动进入 ACTIVE / COOLDOWN / DEPRECATED 状态
* 防止历史规则长期污染决策空间

系统不仅会“学习”，还会 **主动遗忘**。

---

## 11. 可解释性与可视化

browser4agi 内建多种可视化视角：

* WorldModel Version DAG
* Patch Lineage
* Rule Heatmap

这使系统行为对人类工程师 **完全透明、可调试、可审计**。

---

## 12. 意义与扩展

browser4agi 不只是一个浏览器 Agent，而是一种 **Self-Evolving Control System** 的实例：

* 可迁移到 API 调用 Agent
* 可迁移到 DevOps / 自动运维
* 可作为研究长期 Agent 演化的实验平台

---

## 13. 结论

browser4agi 证明了一点：

> **真正可扩展、可维护的 Agent，不是“更聪明”，而是“更自律”。**

通过执行优先、失败驱动、模拟约束与全局预算控制，browser4agi 展示了一条区别于纯 LLM Agent 的技术路线，为长期自主智能体提供了工程化答案。

---
