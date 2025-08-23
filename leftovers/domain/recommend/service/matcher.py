import numpy as np
from leftovers.domain.recommend.service import loader

# 메뉴 이름이 유사한 것 찾기
def match_top1(query: str):
    if not loader._NAME_LIST or loader._HNSW_INDEX : # 로딩된 메뉴가 없을 경우, ANN 인덱스가 없을 경우
        return (-1, "", 0.0) # 매칭 실패
    
    if query in loader._NAME_LOOKUP: # 입력이 DB에 있는 경우 transform 스킵
        query_vector = loader._NAME_LOOKUP[query].astype(np.float32).reshape(1, -1)
    else:
        query_vector = loader._NAME_VEC.transform([str(query)]).astype(np.float32)
    
    labels, distances = loader._HNSW_INDEX.knn_query(query_vector, k=1)
    idx = int(labels[0][0])
    similarity = 1 - float(distances[0][0]) # 가장 높은 유사도를 가진 인덱스

    if not np.isfinite(similarity): # NaN이나 inf 나오면
        similarity = 0.0 # 0.0.으로 보정
    return (idx, loader._NAME_LIST[idx], similarity)