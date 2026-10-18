# 口播改造的来源与边界

用于核对方法依据；不必每次写稿全读。以下是研究结论与工程借鉴的区分，不能给整个skill背书为“已科学验证”。来源核查于2026-10-13。

## 学术证据

- **Ginns, Martin & Marsh (2013), Designing Instructional Text in a Conversational Style: A Meta-analysis, Educational Psychology Review 25:445–472.** [出版社摘要](https://link.springer.com/article/10.1007/s10648-013-9228-0)。对话式语言对保持与迁移有显著平均效应，兴趣平均效应不显著；超过35分钟的研究效果小且不显著。支持分别检验自然度、理解与兴趣，不能把35分钟当注意力阈值，也不能直接保证中文长讲座受益。此处核对的是摘要，不宣称全文评审。
- **Singh, Marcus & Ayres (2012), The Transient Information Effect: Investigating the Impact of Segmentation on Spoken and Written text, Applied Cognitive Psychology 26:848–853.** [出版社摘要](https://onlinelibrary.wiley.com/doi/10.1002/acp.2885)。两项十年级学生实验支持将解释分成有意义的小段，口头材料尤其受益。不由此制定中文句长或固定停顿秒数。
- **Hwang et al. (2023), Rewriting the Script: Adapting Text Instructions for Voice Interaction, DIS 2023.** [作者全文](https://arxiv.org/html/2306.09992v1)。12人烹饪语音指导观察提出拆分、重排、路标等转换方法。借鉴书面转口头的信息组织，不声称其已验证大学讲座效果。
- **Flowerdew & Tauroza (1995), The Effect of Discourse Markers on Second Language Lecture Comprehension.** [出版社摘要](https://doi.org/10.1017/S0272263100014406)。保留自然讲座的话语标记，相对删掉标记有利于第二语言理解。支持保留有意义的路标，不证明添加语气词越多越好。卷期年份为1995，网页上线年份不是研究年份。

## 实践指导

- [TED官方讲者准备指南](https://www.ted.com/tedx/organizer-guide/prepare-speakers-and-program)：对话式语气、录音—转写—编辑—练习。采用试讲循环，不将TED时长、表演或叙事习惯设为所有课程标准。
- [Columbia Writing for the Ear](https://teachwithds.sandbox.library.columbia.edu/podcasting/writing-for-the-ear/)：听众不能像读者那样回看，句法和信息组织要适合听觉。借鉴单一主意和口头路标；公众播客的规模类比、语体建议需按受众判断。

## GitHub实现参考

以下只借鉴方法，用本skill自有措辞编写规则。星数和安装量不证明教学效果；不要求安装或执行这些仓库。

- [your-voice / human-expression](https://github.com/parasdoshicom/your-voice/blob/main/references/human-expression.md)及[评测方法](https://github.com/parasdoshicom/your-voice/blob/main/references/evaluation.md)：一次听懂、呼吸组、真实声音样本和分维度盲评。仓库MIT；不直接搬用其量化评测阈值。
- [shuorenhua](https://github.com/MrGeDiao/shuorenhua/blob/main/SKILL.md)：中文编辑时保留主体、数值、条件、否定、关系和必要重复。仓库MIT；局部清理不能代替完整口头重组。
- [humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md)：审查刻意反差、强制三分与重复收尾。仓库MIT；不采用AI检测分数、禁词命中或句长分布作为质量证明。
- [presentation-script-coach / natural-speech-guide](https://github.com/archlizheng/presentation-script-coach/blob/main/references/natural-speech-guide.md)：事实保护、独立自然度审稿和样本校准。核查时未确认许可证，仅参考思路，不复制原文或脚本；不引入其全套审批流程。
- [technical-video-script](https://github.com/samber/developer-relations-skills/blob/main/skills/technical-video-script/SKILL.md)：按时间组织解释、音频可理解、讲者实测速率。仓库MIT；视频留存规律不能当作课堂学习效果。

本skill的分工、检查步骤和回归样例是基于上述来源与实际失败形成的工程方案，应持续接受讲者和目标听众的检验。
