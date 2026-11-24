# OpenClash 低倍率下载分流模板

基于 [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) **重度分流版（Custom_Clash_Full.ini）** 自动生成的模板，只做两处改动：

1. **`🐢 低倍率节点` 组**
   - 类型：`smart` → `fallback`
   - 成员：只取节点名里倍率 ≤ 0.6 的节点（`0.01`、`0.5`、`0.6` 都算，`0.8` 及以上不算）
   - 末尾兜底：`🚀 手动选择`
2. **`🚀 手动选择` 组**：去掉对 `🐢 低倍率节点` 的引用，避免 fallback 形成策略组环（内核会拒绝加载）。

## 自动更新

`.github/workflows/build.yml` 每 10 分钟拉一次上游 full 版，套用上面的改动后写回 `out/`；内容有变化才提交，所以这里永远是「上游最新 + 本地自定义」的结果，不需要手工同步。

如果上游改了组名导致匹配不到，脚本会直接报错退出，工作流变红，文件保持上一次可用的版本，不会静默生成错误模板。

## 使用

OpenClash → 订阅 → 编辑该订阅：

- 模板：选「自定义模板 / Custom Template」
- 自定义模板地址：

```
https://raw.githubusercontent.com/s890214/openclash-lowmult-template/main/out/Custom_Clash_Full_LowMultiplier.ini
```

改完保存并更新订阅即可。

## 本地运行

```bash
python3 build.py
```

输出：`out/Custom_Clash_Full_LowMultiplier.ini`
