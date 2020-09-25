# Exploration

!> 限于计算资源，后续探索将无限延期，也许会鸽掉，下面记录此前的简单探索，以便恢复进行时快速进入状态

## 计划

- 无标签生成
   - DCGAN
   - Style GAN/Style GAN2 生成
- 有标签生成
   - ACGAN

## 进度

前几个版本内有着我用来弥补上一个项目的遗憾的一些代码，主要是用于系统化的配置解析、Cache 机制，但最近发现使用 Jupyter 进行实验可能会更方便一些，所以移除了这些代码

另外，前几个版本也有数据爬去及预处理的代码，暂时也移除了，数据预处理后需要花费大量时间进行数据清洗，如果不是要做大项目，还是不建议自己获取数据的

模型的话，仅仅完成 DCGAN （TensorFlow2.2）的简单实现，但尚不知是 DCGAN 搭建及训练方式有问题还是其他问题，当前还无法生成能看的图片（即便只有 64*64）

## 可能的问题

- DCGAN 搭建错误（TensorFlow 总是会存在莫名其妙的问题，也许下次我果断转 Pytorch）
- 学习率的问题，尝试的还不是特别多，仅限于 1e-5~2e-4 的范围，且未仔细比较
- loss 的问题，没成功 print loss，因此还没仔细对比，也许是 Discriminator train 得太好导致 Generator 没有梯度？也许需要调节两者的训练次数（有尝试过，但仅根据 D 的分类准确率进行评估，因此可能不是很合理）

# References

1. [利用GAN生成动漫头像](https://blog.csdn.net/qq_34739497/article/details/79902356)
2. [基于GAN的动漫头像生成](https://zhuanlan.zhihu.com/p/76340704)