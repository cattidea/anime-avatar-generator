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

> 约定
> - 配置的 key 不带中划线 `-`，尽量使用下划线 `_`

## 文档预览

使用 `Docsify` 方便快捷地生成文档站点，只需要使用以下命令即可实时预览内容（改动后需刷新），无需安装任何依赖

``` bash
python docs
```

## 通用缓存

可通过装饰器 `CacheLoader` 简单地对数据获取函数增加一个本地 Cache

!> 请确定 keymap 能根据参数得到唯一的 hash（决不可带 random）

``` python
@CacheLoader()
def get_sum(a=1, b=1):
   return a + b
```

> 约定
> - 函数名使用 `get_` 开头
> - 使用通用 keymap 时绑定的文件与文件夹均应以 `kwargs` 方式传入，且 key 应分别以 `_file` 与 `_dir` 结尾
