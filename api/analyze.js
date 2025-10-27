export default async function handler(req, res) {
  // 1) 메서드 체크: POST만 허용
  if (req.method !== "POST") {
    return res
      .status(405)
      .json({ error: "POST만 가능해요. Use POST method." });
  }

  // 2) body 꺼내기
  // Vercel에서는 req.body가 이미 파싱돼 있을 수도 있고,
  // 아닐 수도 있어서 둘 다 처리해볼게.
  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch (e) {
      return res.status(400).json({ error: "JSON 파싱 실패" });
    }
  }

  // records 배열 확인
  const records = body?.records;
  if (!Array.isArray(records)) {
    return res.status(400).json({ error: "records 배열이 필요해요" });
  }

  // 3) 총지출 / 카테고리별 합계 계산
  let total = 0;
  const categorySum = {};

  for (const item of records) {
    // 우리가 보낸 JSON은 "카테고리", "금액" 이런 한글 key를 쓰고 있지?
    const category =
      item["카테고리"] ?? item["category"] ?? item["분류"] ?? "기타";

    const amount =
      item["금액"] ?? item["amount"] ?? item["price"] ?? 0;

    // 숫자화
    const money = Number(amount) || 0;

    total += money;
    categorySum[category] = (categorySum[category] || 0) + money;
  }

  // 4) 결과 리턴
  return res.status(200).json({
    "총지출": total,
    "카테고리별": categorySum,
  });
}
