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

### Latent Attention
路径： language2code/baselines/Latent-Attention/
为Xinyun Chen等所著Latent Attention For If-Then Program Synthesis中提及代码  
源码原地址为[https://github.com/Jungyhuk/Latent-Attention](https://github.com/Jungyhuk/Latent-Attention)  
#### 数据处理、训练  
除了使用原数据进行复现外，也使用了自己爬取的数据进行了测试，数据处理脚本为process_IFTTT_data_new.py，使用方法为  
```
python2.7 process_IFTTT_data_new.py --input-file ../../ifttt_data/coreresult.tsv --output data.pkl
```
这样可以生成一个用于训练的数据集，训练方法如同原repo中所提及的  
```
python2.7 train.py --dataset data.pkl --config configs/model.jsonnet --logdir model --output result
```
这里dataset指向刚才生成的数据集即可，训练完的模型会以checkpoint的形式保存在model文件夹下  
#### RESTful API  
另外实现了一个RESTful API，使用训练好的模型进行预测  
首先对data.pkl进行精简，删去其中的训练、验证、测试数据，得到data_util.pkl，然后需要在model中选定一个checkpoint作为预测用的模型  
假设这个checkpoint的meta文件为model.ckpt-0.meta，那么启动API的方式为  
```
python2.7 RESTful.py --config configs/model.jsonnet --dataset util_data.pkl --load-model model/model.ckpt-0
```
注意load-model里文件名要把.meta之类的后缀去掉，这样之后API就会在127.0.0.1启动，具体端口会在log中显示  
请求方法：向http://127.0.0.1:port/Latent 发送post请求，格式为{'input_str': string}，输入自然语言，API会以json方式返回预测出的IFTTT recipe  
以curl为例，如果想要预测hello这个自然语言对应的IFTTT recipe    
```
curl -d "input_str=hello" http://127.0.0.1:pppp/Latent 
```
而在运行API的地方也会打印出一个http 200的信息
