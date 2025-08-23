import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from leftovers.domain.recommend.service import loader

# 메뉴 이름이 유사한 것 찾기
def match_top1(query: str):
    if not loader._NAME_LIST: # 로딩된 메뉴가 없을 경우
        return (-1, "", 0.0) # 매칭 실패
    
    query_vector = loader._NAME_VEC.transform([str(query)]) # 문자열을 벡터로 변환
    similarity_list = linear_kernel(query_vector, loader._NAME_MAT).ravel() # 두 벡터 간의 유사도 측정
    idx = int(np.argmax(similarity_list)) # 가장 높은 유사도를 가진 인덱스
    similarity = float(similarity_list[idx])

    if not np.isfinite(similarity): # NaN이나 inf 나오면
        similarity = 0.0 # 0.0.으로 보정
    return (idx, loader._NAME_LIST[idx], similarity)