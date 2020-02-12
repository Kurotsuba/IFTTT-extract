# IFTTT-extract  
  
## Introduction  
本项目目的在于从自然语言中抽取出IFTTT任务规则。  
结合领域知识图谱以及程序检索、机器翻译以及强化学习的方法，得到如下六个字段：  
- Trigger Channel   
- Trigger Function  
- Trigger Attribute
- Action Channel  
- Action Function  
- Action Attribute  

## Baselines
作为项目基线，已经实现了程序检索以及机器翻译的方法，保存在baselines文件夹中

### 数据准备
源数据来自于 [http://research.microsoft.com/lang2code/](http://research.microsoft.com/lang2code/) ，解压后保存在 language2code/ifttt_data 中  
对其中的 data/turk_public.tsv 运行preprocess.py ，可得到data.pickle

### Program Retrieval
路径： language2code/baselines/retrival/  
基于Chris Quirk等所著Language to Code: Learning Semantic Parsers for If-This-Then-That Recipes中4.1描述进行实现  
通过edit distance作为相似度评判指标进行程序检索，程序会读取data.pickle作为数据源  
使用python3.6运行code.py，按照提示输入想要输入的description，即可返回最终结果  
在使用已保存的数据进行测试时，准确率为100%，使用未保存的数据进行测试，会返回近似的结果，但是缺乏实际意义  

### Machine Translation  
路径： language2code/baselines/NMT/  
按照Chris Quirk等所著Language to Code: Learning Semantic Parsers for If-This-Then-That Recipes中4.2描述进行实现  
该实现依赖于pytorch，python3.6  
一个简单的Encoder-Decoder RNN 机器翻译实现，读取data.pickle作为平行语料数据源  
使用python3.6运行code.py，即可完成训练、测试  
限定描述句长为25时，准确率为90%左右  

### Interactive Sementic Parsing
路径： language2code/baselines/Interactive-Sementic-Parsing/  
为Ziyu Yao等所著Interactive Semantic Parsing for If-Then Recipes via Hierarchical Reinforcement Learning中所提及代码  
源码原地址为 [https://github.com/LittleYUYU/Interactive-Semantic-Parsing](https://github.com/LittleYUYU/Interactive-Semantic-Parsing)  
克隆下来之后按照原repo中readme进行运行，准确率为95%左右
