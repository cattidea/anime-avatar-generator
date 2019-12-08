# Avatar Generater

GAN 头像生成器

!> Status: WIP

## 配置解析

可以方便地使用命令参数对配置进行修改

比如，`--docs-base=/test/` 便可修改 `config.json` 中的配置

``` diff
{
   "docs": {
      "base": "/test/"
   }
}
```

当然，配置文件并不会被修改，仅仅会修改配置流程中的值

## 文档预览

使用 `Docsify` 方便快捷地生成文档站点，只需要使用以下命令即可实时预览内容（改动后需刷新），无需安装任何依赖

``` bash
python docs
```
