<div align="center">
  <h1>Graph DataGen</h1>
</div>

本项目是一个为图数据库使用者自动生成测试数据集的工具，通过简单配置自己业务场景中的图结构和生成规则，运行本项目所提供的脚本就能自动生成指定规模并且贴近真实场景的数据集，为快速进行方案验证和性能测试提供帮助。

# 如何使用

[English](README_en.md)

**使用方式**：需要先在yaml文件中手动配置图空间的schema结构，运行main.py后会在指定的目录下生成csv格式的测试数据集，此数据集是根据nebula-importer工具要求的格式来生成，可以直接使用nebula-importer工具将数据集导入nebula-graph中。

## 环境准备
 * 运行环境：python 3.8+
 * 安装项目依赖：pip install -r requirements.txt
 * 环境变量：将PYTHONPATH设置到项目目录下, 例如：/Users/[XXX]/Downloads/graph-datagen

## 规则配置
配置文件config.yaml中主要有两块内容：
 * **clientSettings**: 运行配置，包括并发线程数，任务缓存队列大小，生成数据的目标语言； 
 * **graph**: 图的点、边结构以及每个点/边生成数量大小，还包括每个字段属性的生成方式； 

### I.图结构配置
graph中每个节点表示图DB中的一个点或一条边，每个节点都有两部分配置：
 - **schema**：节点结构、生成数量及生成规则配置
 - **output**：节点数据的输出配置，目前暂且只支持了csv一种格式； 

schema中有三部分组成：
 1. **节点结构**：与自开源nebula-importer工具的节点配置定义相同，可直接参考：[Nebula Importer Schema配置](https://docs.nebula-graph.com.cn/3.3.0/nebula-importer/use-importer/#schema)
 2. **生成数量**，点和边的配置有所区分：
    - **vertex**: 为每个点扩展了genNum参数用于表示此节点要生成的总数量； 
    - **edge**: 为每条边扩展了一个预定义属性genNumPerVID，用于配置每个srcVID出发要生成同类型但不同dstVID的边数量，这样配置是为了让边的数量更贴近业务场景，因为边反映的是一个点与其它点之间的业务联系； 
 3. **生成规则**：在每个属性上扩展一个genrule表示此属性的生成规则，具体下面会详细介绍；

### II.生成规则配置
genrule接受的是一个字典结构配置，配置的字段主要分为两部分：
 - **generator**: 所选生成器，本质上是一个生成数量的方法名，调用方法即可生成相应类型的数量
 - **生成器参数**：除generator外的所有参数都会被认为是生成器参数，会作为命名参数传给生成器
 
目前支持的generator分为两大类：
1. **faker自带生成器**，项目中约定：faker方法名就是生成器名称，方法参数就是生成器参数，统一以命名参数来配置；例如：
    * random_int：     指定最小、最大值范围的随机整数，接受min和max参数表示数字的随机范围
    * ramdom_number：  指定长度的数字串，接受digits表示要生成的数字长度； 
    * random_element： 指定列表范围内随机返回一个元素，接受elements（tuple类型）表示可选列表
    * name：           人名，例如：张三
    * sentence：       指定字长的句串，例如：如何自动生成数据
    * company：        公司名称，例如：合联电子信息有限公司
    * ……
2. **自定义生成器**：基于图结构需求补充扩展的自定义生成器，目前包括下面几个：
    * id：             ID递增序列，对应日常业务开发中的数据唯一标识（整数），可以结合prefix来生成str类型的唯一标识
    * const:           定值常量,可以是整数也可以是字符串，例如：4，"E"
    * reference:       引用变量,例如：a_{user_id}，这个变量必须在同一个schema下
    * eval:            计算表达式，例如：start_time+duration
    * oftag:           从已有tag中取点ID，只适用于生成边的srcVID和dstVID场景，基于边的srcVID和dstVID必须是在点中存在的； 

faker是一个开源的数据mock项目，上面faker自带生成器只列了很小一部分，更多生成器参考：[faker.providers](https://faker.readthedocs.io/en/master/providers/baseprovider.html)

 ## 运行脚本
 终端运行： ./main.py --config config.yaml

 ## 实践记录
**示例**：项目的examples目录下两个场景的配置文件示例可供参考，可以直接运行：
 - config_course.yaml: 学生选课业务
 - config_event.yaml: 活动推荐业务

**关于执行耗时**：两百万规模的数据大概需要100秒左右，两千万规模的数据大概需要1100秒左右； 

**关于多线程并发**：项目配置文件中虽然支持num_workers配置工作线程数，不过经过实践，python中并发多线程对于加快运行效率作用不太明显，原因后来才得知是python中有全局解释器锁（GIL）的限制，多线程并不能利用多核心； 

**关于设计思路**，请参考：https://blog.csdn.net/xiaojia1001/article/details/131027997