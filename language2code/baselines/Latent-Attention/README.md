# Latent Attention For If-Then Program Synthesis

## Original Readme 
原项目的Readme文档位置在[这里](https://github.com/Jungyhuk/Latent-Attention/blob/master/README.md)可以找到，由于我修改了代码，用原来的流程可能无法顺利运行项目，如果有需要请使用[原项目](https://github.com/Jungyhuk/Latent-Attention)

## 前置需求 
python2.7 
sklearn 
jsonnet 
TensorFlow v1.14 

## 数据集
源数据为ifttt_data/coreresults.tsv，使用process_IFTTT_data_xxx.py可以对应的得到不同类型的数据，如想要得到包含用户信息的数据集，可以使用 

	python2.7 process_IFTTT_data_user.py --input-file ../../ifttt_data/coreresults.tsv --output data_user.pkl

为了开发方便也可以使用小一些的数据，在ifttt_data下有一个toyresults.tsv，替换入input-file参数即可

## 知识图谱
使用了部署在实验室服务器的知识图谱，如果没有这个知识图谱也可以运行，但是效果会比较差

## 运行
目前可以直接运行的有两个方案：使用知识图谱进行修正的autofix，以及再其基础上加入用户信息修正的user_autofix 
如果想要运行autofix方案  

	python2.7 train_autofix.py --dataset data.pkl --config configs/model.jsonnet --logdir model --output result
如果想要运行user_autofix方案  

	python2.7 train_user_autofix.py --dataset data_user.pkl --config configs/model.jsonnet --logdir model --output result
训练出的模型会保存在model文件夹中，user_autofix方案的数据必须含有用户信息，也就是使用process_IFTTT_data_user.py处理处的数据才可以