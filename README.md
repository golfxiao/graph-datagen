<div align="center">
  <h1>Graph DataGen</h1>
</div>

The purpose of this project is to automatically generate test datasets for graph databases. By configuring the graph structure and generation rules in your own business scenario, you can run the scripts provided by this project to generate datasets that are close to real scenarios and of a specified scale, which helps to quickly verify solutions and perform performance testing.

# How to use

[CN](README_cn.md)

## Environment Preparation
* Runtime environment: Python 3.8+
* Install project dependencies: pip install -r requirements.txt
* Environment variables: Set PYTHONPATH to the project directory, for example: /Users/[XXX]/Downloads/graph-datagen

## Rule Configuration
The config.yaml file contains two main sections:
* **clientSettings**: runtime configuration, including the number of concurrent threads, task cache queue size, and target language for generating data;
* **graph**: the structure of the graph's nodes and edges, the size of each node/edge generated, and the generation method for each field attribute.

### I. Graph Structure Configuration
Each node in the graph represents a point or an edge in the graph database, and each node has two parts of configuration:
- **schema**: node structure, generation quantity, and generation rule configuration
- **output**: output configuration for node data, currently only supporting the csv format

The schema consists of three parts:
1. **Node structure**: the same as the node configuration definition of the open-source Nebula Importer tool, which can be directly referenced at: [Nebula Importer Schema Configuration](https://docs.nebula-graph.com.cn/3.3.0/nebula-importer/use-importer/#schema)
2. **Generation quantity**: there are differences in the configuration of points and edges:
   - **vertex**: the genNum parameter is extended for each point to indicate the total number of nodes to be generated for this node;
   - **edge**: a predefined attribute genNumPerVID is extended for each edge to configure the number of edges of the same type but different dstVID to be generated for each srcVID. This configuration is to make the number of edges closer to the business scenario, as edges reflect the business connections between a point and other points.
3. **Generation rules**: a genrule is extended on each attribute to indicate the generation rule for this attribute. The details will be introduced below.

### II. Generation Rule Configuration
The genrule accepts a dictionary structure configuration, and the configured fields are mainly divided into two parts:
- **generator**: the selected generator, which is essentially a method name for generating the quantity, and calling the method can generate the corresponding type of quantity.
- **Generator parameters**: all parameters except generator are considered generator parameters and will be passed as named parameters to the generator.

Currently, the supported generators are divided into two categories:
1. **Faker built-in generators**. It is agreed in the project that the faker method name is the generator name, and the method parameters are the generator parameters, which are uniformly configured as named parameters. For example:
   - **random_int**: generates a random integer within a specified range, accepts min and max parameters to indicate the range of numbers to be generated.
   - **random_number**: generates a string of specified length, accepts digits to indicate the length of the number to be generated.
   - **random_element**: randomly returns an element within a specified list range, accepts elements (tuple type) to indicate the optional list.
   - **name**: generates a person's name, for example: Zhang San.
   - **sentence**: generates a sentence of specified length, for example: How to generate data automatically.
   - **company**: generates a company name, for example: HeLian Electronic Information Co., Ltd.
   - ...
2. **Custom generators**: custom generators based on graph structure requirements. Currently, there are several types:
   - **id**: an ID incremental sequence, corresponding to the unique identifier (integer) of data in daily business development. It can be combined with prefix to generate a unique identifier of str type.
   - **const**: a constant value, which can be an integer or a string, for example: 4, "E".
   - **reference**: a reference variable, for example: a_{user_id}, this variable must be in the same schema.
   - **eval**: a calculated expression, for example: start_time+duration.
   - **oftag**: takes the point ID from an existing tag, only applicable to the scenario of generating srcVID and dstVID of edges, and the srcVID and dstVID of edges must exist in the points.

Faker is an open-source data mocking project, and only a small part of the built-in generators are listed above. For more generators, please refer to the documentation：[faker.providers](https://faker.readthedocs.io/en/master/providers/baseprovider.html)

## Running the Script
Run in the terminal: ./main.py --config config.yaml

## Quick Practice
**Example**: Two configuration file examples for different scenarios are available in the examples directory of the project, which can be run directly:
- config_course.yaml: student course selection business
- config_event.yaml: activity recommendation business

**About Running Time**: Generating data of a scale of two million takes about 110 seconds, and generating data of a scale of twenty million takes about 1100 seconds.

**About Multi-threading**: Although the project configuration file supports the num_workers configuration of working threads, after practice, multi-threading concurrency in Python does not have a significant effect on improving running efficiency. The reason is that Python has a global interpreter lock (GIL) restriction, and multi-threading cannot utilize multiple cores.

**About Multi-processing**: We have considered introducing multi-processing to fully utilize CPU multi-core, but after research, we did not introduce it mainly for the following reasons:
- Multi-process programming has a certain complexity and requires a set of specialized APIs so that multiple processes can communicate and pass data to each other, which makes program understanding and maintenance difficult.
- Introducing multi-processing may not improve the performance of this project as expected, mainly because multi-processing does not share memory space, and the overhead of copying massive data in memory may offset the improvement brought by multi-core parallelism.

## Possible Future Plans

In the future, an article may be written to introduce the design process and operation flow of this tool, and some feature extensions will also be made. Two possible meaningful feature extension directions that we have thought of are::
1. Support docking with graph databases to read the point and edge structures in the specified graph space to automatically generate the graph schema configuration.
2. Support more types of graph database data formats.

If you encounter any problems or have constructive criticism and suggestions while using this tool, please feel free to leave a message.
