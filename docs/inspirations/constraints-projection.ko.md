# Constraints Projection (제약 투영)

[English](constraints-projection.md) | **한국어**

기존 관료적 소프트웨어 공학은 인간의 인지 한계로 인해 '사후 유지보수'와 '하방 방어'에 치중했습니다. 반면 **Constraints Projection**은 LLM의 패턴 매칭 및 전수 탐색 능력을 전제로, 극단적인 이상 상태(Ideal Oracle)에서 시작해 현실 제약을 단계별로 투영(Project)하여 실행 가능한 구현체를 수렴시키는 AI 네이티브 개발 패러다임입니다.

---

## 1. 패러다임 전환

| 구분 | 전통적 개발 방식 (Human-Centric) | Constraints Projection (AI-Native) |
| --- | --- | --- |
| **출발점** | 현실 제약(언어, 프레임워크, 리소스) 기반 설계 | 무비용·무입력의 이상적 오라클 모델 ($f() \to Output$) |
| **주요 동력** | 인간 직관에 의한 사전 예외 처리 및 방어적 코딩 | AI 기반 이상 가정 열거 $\to$ 물리/시스템 제약 매핑 |
| **목표** | 실패 방어 및 책임 소재 분산 (하방 지지) | 이상 상태와 물리 한계 간의 최적 타협점 도출 |

---

## 2. 작동 프로세스

어텐션 희석(Attention Dilution)을 방지하기 위해 각 단계는 엄격히 분리된 컨텍스트에서 순차 실행합니다.

```text
[Phase 1: Ideal Assumption] --> [Phase 2: Constraints Identification] --> [Phase 3: Projection & Action]
    (현실 한계 배제)                   (물리/비즈니스 제약 열거)                  (수용 / 타협 / 포기)

```

### Phase 1. 이상적 오라클 상정 (Ideal Assumptions)

현실 구현 가능성을 배제하고, 입력·지연·비용이 0인 상태에서 원하는 결과만 나오는 이상 상태를 도출합니다.

```python
def solve():
    return do_anything_you_want()  # 즉각 처리, 비용 0, 부작용 0

```

* **가정 1 (Zero Input):** 입력 파라미터나 상태 조회 없이 시스템이 맥락을 즉각 인지한다.
* **가정 2 (Instant Execution):** 복잡도 $O(1)$, 지연 시간 $0\text{ms}$로 연산이 종료된다.
* **가정 3 (Unlimited Resource):** 메모리, 대역폭, API 비용이 무제한이다.
* **가정 4 (Zero State Drift):** 동시성 충돌이나 데이터 유실이 원천 차단된다.

### Phase 2. 제약 식별 (Constraints Identification)

각 가정에 충돌하는 현실적 경계(물리 법칙, 하드웨어, 비즈니스 규칙)를 독립적으로 매핑합니다.

* **제약 A:** 분산 노드 간 네트워크 RTT 및 대역폭 한계
* **제약 B:** 사용자 입력 부재 시 발생 가능한 모호성(Ambiguity)
* **제약 C:** 외부 인프라 및 LLM 호출 비용 한도

### Phase 3. 제약 투영 (Projection & Decision)

가정에 제약을 투영하여 최종 시그니처와 구현 방식을 결정합니다.

* **가정 1 (Zero Input) $\to$ [타협]**
* *결정:* 필수 식별자만 입력으로 수용하고, 파생 컨텍스트는 로컬 캐시에서 자동 주입.

* **가정 2 (Instant Execution) $\to$ [포기]**
* *결정:* $0\text{ms}$ 불가능. 비동기 큐(`Job/Worker`) 기반 Eventual Consistency로 전환.

* **가정 3 (Zero State Drift) $\to$ [수용]**
* *결정:* 불변 이벤트 스트림(Event Sourcing)을 적용하여 상태 드리프트 배제.

---

## 3. 기존 코드베이스 적용 (Incremental Projection)

기존 기능 확장 시에는 "기존 입력 유지 + 목표 출력 달성 + 추가 비용 0"을 기본 이상 가상선으로 설정합니다.

1. **Ideal Delta:** 기존 $f(x)$가 수정 없이 즉시 $f'(x) \to y'$를 부작용 없이 반환한다고 가정.
2. **Projection:**

* 인터페이스 호환성 제약 투영 $\to$ 기존 호출자(Caller) 파괴 불가 확인.
* 성능 제약 투영 $\to$ 동기 연산 불가 확인.

1. **Result:** 어댑터 패턴 적용 및 백그라운드 태스크 분리를 통한 점진적 수렴.

---

## 4. 왜 AI에 적합한가

* **조합 폭발 처리:** 인간은 이상 가정과 제약의 다대다 매핑 시 인지 부하가 급증하지만, LLM은 방대한 제약 매트릭스를 누락 없이 전수 교차 검증합니다.
* **선입견 배제:** 개발자가 "어차피 안 된다"고 조기 기각하던 최적 아키텍처를 이상 상태에서 역추적하여 발굴합니다.

---

## 5. 실행 파이프라인 설계 (어텐션 희석 방지)

단계 혼재로 인한 성능 저하를 방지하기 위해 컨텍스트를 파이프라인 단위로 격리합니다.

1. **Pipeline-1 (Generator):** 오직 이상 가정만 열거 (현실 제약 언급 금지 프롬프트).
2. **Pipeline-2 (Critic):** 시스템 명세, 물리 제약, 런타임 환경 매핑.
3. **Pipeline-3 (Resolver):** 1과 2를 대조하여 각 가정별 수용/타협/포기 판단 및 최종 구현 명세 생성.
