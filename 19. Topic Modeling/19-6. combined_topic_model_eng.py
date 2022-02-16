# -*- coding: utf-8 -*-
"""Combined Topic Model을 이용한 토픽 모델링

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ccFbeVmXapSN79AYLT0QQwybBLHjL7Wy

# 복합 토픽 모델링(Combined Topic Modeling)

이 튜토리얼에서는 복합 토픽 모델(**Combined Topic Model**)을 사용하여 문서의 집합에서 토픽을 추출해보겠습니다.

## 토픽 모델(Topic Models)

토픽 모델을 사용하면 비지도 학습 방식으로 문서에 잠재된 토픽을 추출할 수 있습니다.

## 문맥을 반영한 토픽 모델(Contextualized Topic Models)
문맥을 반영한 토픽 모델(Contextualized Topic Models, CTM)이란 무엇일까요? CTM은 BERT 임베딩의 표현력과 토픽 모델의 비지도 학습의 능력을 결합하여 문서에서 주제를 가져오는 토픽 모델의 일종입니다.


## 파이썬 패키지(Python Package)

패키지는 여기를 참고하세요 [링크](https://github.com/MilaNLProc/contextualized-topic-models).

![https://github.com/MilaNLProc/contextualized-topic-models/actions](https://github.com/MilaNLProc/contextualized-topic-models/workflows/Python%20package/badge.svg) ![https://pypi.python.org/pypi/contextualized_topic_models](https://img.shields.io/pypi/v/contextualized_topic_models.svg) ![https://pepy.tech/badge/contextualized-topic-models](https://pepy.tech/badge/contextualized-topic-models)

# **시작하기 전에...**

이 튜토리얼과 관련하여 추가적인 의문 사항이 있다면 아래 링크를 참고하시기 바랍니다:

- 영어가 아닌 다른 언어로 작업하고 싶으시다면: [여기를 클릭!](https://contextualized-topic-models.readthedocs.io/en/latest/language.html#language-specific)
- 토픽 모델에서 좋은 결과가 나오지 않는다면: [여기를 클릭!](https://contextualized-topic-models.readthedocs.io/en/latest/faq.html#i-am-getting-very-poor-results-what-can-i-do)
- 여러분의 임베딩을 사용하고 싶다면: [여기를 클릭!](https://contextualized-topic-models.readthedocs.io/en/latest/faq.html#can-i-load-my-own-embeddings)

# GPU를 사용하세요

우선, Colab에서 실습하기 전에 GPU 설정을 해주세요:

- 런타임 > 런타임 유형 변경을 클릭하세요.
- 노트 설정 > 하드웨어 가속기에서 'GPU'를 선택해주세요.

[Reference](https://colab.research.google.com/notebooks/gpu.ipynb)

# Contextualized Topic Models, CTM 설치

contextualized topic model 라이브러리를 설치합시다.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install contextualized-topic-models==2.2.0

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install pyldavis

"""## 노트북 재시작

원활한 실습을 위해서 노트북을 재시작 할 필요가 있습니다.

상단에서 런타임 > 런타임 재시작을 클릭해주세요.

# 데이터

학습을 위한 데이터가 필요합니다. 여기서는 하나의 라인(line)에 하나의 문서로 구성된 파일이 필요한데요. 우선, 여러분들의 데이터가 없다면 여기서 준비한 파일로 실습을 해봅시다.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !wget https://raw.githubusercontent.com/vinid/data/master/dbpedia_sample_abstract_20k_unprep.txt

!head -n 1 dbpedia_sample_abstract_20k_unprep.txt

!head -n 3 dbpedia_sample_abstract_20k_unprep.txt

!head -n 5 dbpedia_sample_abstract_20k_unprep.txt

text_file = "dbpedia_sample_abstract_20k_unprep.txt" # EDIT THIS WITH THE FILE YOU UPLOAD

"""# 필요한 것들을 임포트"""

from contextualized_topic_models.models.ctm import CombinedTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from contextualized_topic_models.utils.preprocessing import WhiteSpacePreprocessing
import nltk

"""## 전처리

여기서 전처리 된 텍스트를 사용하는 이유는 무엇일까요? Bag of Words를 구축하려면 특수문자가 없는 텍스트가 필요하고, 모든 단어를 사용하는 것보다는 빈번한 단어들만 사용하는 것이 좋습니다.
"""

nltk.download('stopwords')

documents = [line.strip() for line in open(text_file, encoding="utf-8").readlines()]
sp = WhiteSpacePreprocessing(documents, stopwords_language='english')
preprocessed_documents, unpreprocessed_corpus, vocab = sp.preprocess()

# normalization 전처리 후 문서
preprocessed_documents[:2]

# 전처리 전 문서 == documnets와 동일
unpreprocessed_corpus[:2]

# 전체 단어 집합의 개수
print('bag of words에 사용 될 단어 집합의 개수 :',len(vocab))

vocab[:5]

"""전처리 되지 않은 문서는 문맥을 반영한 문서 임베딩을 얻기 위한 입력으로 사용할 것이기 때문에 제거해서는 안 됩니다.  

전처리 전 문서와 전처리 후 문서를 TopicModelDataPreparation 객체에 넘겨줍니다. 이 객체는 bag of words와 문맥을 반영한 문서의 BERT 임베딩을 얻습니다. 여기서 사용할 pretrained BERT는 paraphrase-distilroberta-base-v1입니다.
"""

tp = TopicModelDataPreparation("paraphrase-distilroberta-base-v1")

training_dataset = tp.fit(text_for_contextual=unpreprocessed_corpus, text_for_bow=preprocessed_documents)

tp.vocab[:10]

len(tp.vocab)

"""단어 집합의 상위 10개 단어를 출력해봅시다. 여기서 출력하는 tp.vocab과 앞에서의 vocab은 집합 관점에서는 같습니다."""

set(vocab) == set(tp.vocab)

"""## Combined TM 학습하기
이제 토픽 모델을 학습합니다. 여기서는 하이퍼파라미터에 해당하는 토픽의 개수(n_components)로는 50개를 선정합니다.
"""

ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, n_components=50, num_epochs=20)
ctm.fit(training_dataset) # run the model

"""# 토픽들

학습 후에는 토픽 모델이 선정한 토픽들을 보려면 아래의 메소드를 사용합니다.

```
get_topic_lists
```
해당 메소드에는 각 토픽마다 몇 개의 단어를 보고 싶은지에 해당하는 파라미터를 넣어즐 수 있습니다. 여기서는 5개를 선택했습니다. 아래의 토픽들은 위키피디아(일반적인 주제)으로부터 얻은 토픽을 보여줍니다. 우리는 영어 문서로 학습하였으므로 각 토픽에 해당하는 단어들도 영어 단어들입니다.
"""

ctm.get_topic_lists(5)

"""# 시각화

우리의 토픽들을 시각화하기 위해서는 PyLDAvis를 사용합니다.
"""

lda_vis_data = ctm.get_ldavis_data_format(tp.vocab, training_dataset, n_samples=10)

import pyLDAvis as vis

lda_vis_data = ctm.get_ldavis_data_format(tp.vocab, training_dataset, n_samples=10)

ctm_pd = vis.prepare(**lda_vis_data)
vis.display(ctm_pd)

"""이제 임의의 문서를 가져와서 어떤 토픽이 할당되었는지 확인할 수 있습니다. 예를 들어, 반도(peninsula)에 대한 첫번째 전처리 된 문서의 토픽을 예측해 봅시다."""

topics_predictions = ctm.get_thetas(training_dataset, n_samples=5) # get all the topic predictions

# 전처리 문서의 첫번째 문서
print(preprocessed_documents[0])

import numpy as np
topic_number = np.argmax(topics_predictions[0]) # get the topic id of the first document

ctm.get_topic_lists(5)[topic_number] #and the topic should be about natural location related things

"""# 차후 사용을 위해 모델 저장하기"""

ctm.save(models_dir="./")

# let's remove the trained model
del ctm

ctm = CombinedTM(bow_size=len(tp.vocab), contextual_size=768, num_epochs=100, n_components=50)

ctm.load("/content/contextualized_topic_model_nc_50_tpm_0.0_tpv_0.98_hs_prodLDA_ac_(100, 100)_do_softplus_lr_0.2_mo_0.002_rp_0.99",
                                                                                                      epoch=19)

ctm.get_topic_lists(5)

"""참고 자료 : https://github.com/MilaNLProc/contextualized-topic-models"""