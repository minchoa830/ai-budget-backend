export default async function handler(req, res) {
  // 1) POST만 허용
  if (req.method !== "POST") {
    return res
      .status(405)
      .json({ error: "POST만 가능합니다." });
  }

  // 2) body 파싱 (문자열일 수도 있고 객체일 수도 있음)
  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch (e) {
      return res.status(400).json({ error: "JSON 파싱 실패" });
    }
  }

  // records 꺼내기
  let records = body?.records;
  if (!Array.isArray(records)) {
    return res.status(400).json({ error: "records 배열이 필요해요" });
  }

  // 3) records 안의 각 항목이 문자열일 수도 있으니까 객체로 변환 시도
  records = records.map((r) => {
    if (typeof r === "string") {
      try {
        return JSON.parse(r); // 문자열이면 JSON으로 다시 파싱
      } catch {
        return {}; // 파싱 실패 시 빈 객체
      }
    }
    return r; // 이미 객체면 그대로
  });

  // 4) 계산
  let total = 0;
  const categorySum = {};

  for (const item of records) {
    // 한글 key, 띄어쓰기 들어간 key까지 커버
    const category =
      item["카테고리"] ??
      item["카 테 고 리"] ??
      item["category"] ??
      "기타";

    const rawAmount =
      item["금액"] ??
      item["금 액"] ??
      item["amount"] ??
      item["price"] ??
      0;

    const money = Number(rawAmount) || 0;

    total += money;
    categorySum[category] = (categorySum[category] || 0) + money;
  }

  // 5) 응답
  return res.status(200).json({
    "총지출": total,
    "카테고리별": categorySum,
  });
}
