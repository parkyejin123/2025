import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, Marker, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Leaf, Sprout, Droplets, FlaskConical, Sparkles, Bird, Bug, Fish, Squirrel, Turtle } from "lucide-react";

// =====================
// 타입 정의
// =====================
type Tree = {
  id: string;
  name: string; // 지역 이름 + 대표수종
  species: string; // 일반명
  scientific?: string; // 학명
  country: string;
  location: [number, number]; // [lat, lng]
  height_m?: number;
  age_years?: number;
  status?: string;
  carbon_t_co2e_per_year?: number; // 연간 탄소흡수량(추정)
  env_benefits?: string[]; // 환경 기여
  env_uses?: string[]; // 환경적 활용/보전 포인트
  image?: string;
  description?: string;
  source?: string;
  lastUpdated?: string;
  growthStage: number; // 0=씨앗,1=새싹,2=어린나무,3=큰 나무
  morningWatered: boolean; // 금일 오전 물
  eveningWatered: boolean; // 금일 저녁 비료
};

// =====================
// 나라 좌표(대략 중심) & 대표 수종 데이터
// =====================
const COUNTRY_CENTER: Record<string, [number, number]> = {
  "Korea, Republic of": [36.5, 127.8],
  Japan: [36.2, 138.2],
  China: [35.9, 104.2],
  "United States": [39.8, -98.6],
  Canada: [56.1, -106.3],
  Brazil: [-10.8, -51.9],
  Australia: [-25.3, 133.8],
  India: [22.9, 79.8],
  Russia: [61.5, 105.3],
  "South Africa": [-30.6, 22.9],
  France: [46.2, 2.2],
  "United Kingdom": [55.4, -3.4],
  Germany: [51.2, 10.4],
};

// 나라별 대표 수종(예시)
const COUNTRY_TREE_INFO: Record<string, Partial<Tree>> = {
  "Korea, Republic of": {
    species: "소나무",
    scientific: "Pinus densiflora",
    carbon_t_co2e_per_year: 0.02,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Pinus_densiflora_in_Korea.jpg/640px-Pinus_densiflora_in_Korea.jpg",
    description: "한반도를 대표하는 상록 침엽수로 사철 푸른 숲을 이룹니다.",
    env_benefits: [
      "도시 미세먼지 저감과 서식지 제공",
      "사계절 산사태 방지에 기여",
    ],
    env_uses: ["방풍림, 조경, 산림복원"],
  },
  Japan: {
    species: "벚나무",
    scientific: "Prunus serrulata",
    carbon_t_co2e_per_year: 0.015,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Cherry_blossoms_in_Tokyo.jpg/640px-Cherry_blossoms_in_Tokyo.jpg",
    description: "봄을 상징하는 수종으로 도시 생물다양성에도 기여합니다.",
    env_benefits: ["곤충 수분활동 촉진", "도시 열섬 완화(그늘 제공)"],
    env_uses: ["도시녹화, 생태관광"],
  },
  China: {
    species: "은행나무",
    scientific: "Ginkgo biloba",
    carbon_t_co2e_per_year: 0.018,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Ginkgo_biloba_JPN.jpg/640px-Ginkgo_biloba_JPN.jpg",
    description: "오염에 강하고 장수하는 수종으로 도시 가로수에 널리 사용됩니다.",
    env_benefits: ["대기오염 저감", "길고 안정적인 탄소 저장"],
    env_uses: ["가로수, 도시숲"],
  },
  "United States": {
    species: "해안세쿼이아",
    scientific: "Sequoia sempervirens",
    carbon_t_co2e_per_year: 10,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Redwood_National_Park%2C_fog_in_the_forest.jpg/640px-Redwood_National_Park%2C_fog_in_the_forest.jpg",
    description: "세계에서 가장 큰 나무 중 하나로 막대한 탄소를 저장합니다.",
    env_benefits: ["대규모 탄소 흡수", "다양한 종의 서식지 제공"],
    env_uses: ["보전 연구, 탄소 모니터링"],
  },
  Canada: {
    species: "전나무",
    scientific: "Abies balsamea",
    carbon_t_co2e_per_year: 0.03,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Abies_balsamea_in_forest.jpg/640px-Abies_balsamea_in_forest.jpg",
    description: "북방 침엽수림을 이루며 광범위한 생태계를 지탱합니다.",
    env_benefits: ["토양보전", "대기정화"],
    env_uses: ["자연보전, 수자원 보호"],
  },
  Brazil: {
    species: "브라질너트나무",
    scientific: "Bertholletia excelsa",
    carbon_t_co2e_per_year: 0.05,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Bertholletia_excelsa.jpg/640px-Bertholletia_excelsa.jpg",
    description: "아마존의 핵심 수종으로 산림의 수분 순환에 기여합니다.",
    env_benefits: ["수분 매개 곤충 서식지 제공", "산림수자원 유지"],
    env_uses: ["비파괴적 임산물(견과) 생산"],
  },
  Australia: {
    species: "유칼립투스",
    scientific: "Eucalyptus spp.",
    carbon_t_co2e_per_year: 0.06,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Eucalyptus_forest.jpg/640px-Eucalyptus_forest.jpg",
    description: "건조 환경에 적응한 상징적 수종으로 토착 동물의 서식지를 제공합니다.",
    env_benefits: ["토착종 서식지", "토양침식 방지"],
    env_uses: ["복원, 방풍"],
  },
  India: {
    species: "망고나무",
    scientific: "Mangifera indica",
    carbon_t_co2e_per_year: 0.025,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Mango_tree_in_India.jpg/640px-Mango_tree_in_India.jpg",
    description: "열대 과실수로 식량과 그늘을 동시에 제공합니다.",
    env_benefits: ["식량 공급", "그늘 제공으로 열섬 완화"],
    env_uses: ["농업-산림 복합, 도시녹화"],
  },
  Russia: {
    species: "가문비나무",
    scientific: "Picea abies",
    carbon_t_co2e_per_year: 0.04,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Picea_abies_forest.jpg/640px-Picea_abies_forest.jpg",
    description: "타이가를 이루는 핵심 수종으로 탄소 저장고 역할을 합니다.",
    env_benefits: ["장기 탄소 저장", "야생동물 서식지"],
    env_uses: ["대규모 산림보전"],
  },
  "South Africa": {
    species: "바오밥",
    scientific: "Adansonia digitata",
    carbon_t_co2e_per_year: 0.03,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Baobab_Trees_Madagascar.jpg/640px-Baobab_Trees_Madagascar.jpg",
    description: "사바나의 물 저장고로 불리며 생태계에 필수적입니다.",
    env_benefits: ["가뭄완화(수분 저장)", "야생동물 먹이 제공"],
    env_uses: ["커뮤니티 기반 보전"],
  },
  France: {
    species: "서양너도밤나무",
    scientific: "Fagus sylvatica",
    carbon_t_co2e_per_year: 0.03,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Beech_forest_in_France.jpg/640px-Beech_forest_in_France.jpg",
    description: "온대 활엽수림의 대표 수종으로 토양과 수자원을 보호합니다.",
    env_benefits: ["수자원 보호", "토양 유기물 축적"],
    env_uses: ["보호구역 관리"],
  },
  "United Kingdom": {
    species: "참나무",
    scientific: "Quercus robur",
    carbon_t_co2e_per_year: 0.035,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Quercus_robur_ancient_oak.jpg/640px-Quercus_robur_ancient_oak.jpg",
    description: "수백 종의 곤충과 균류에 서식지를 제공하는 키스톤 수종입니다.",
    env_benefits: ["생물다양성 증진", "탄소흡수"],
    env_uses: ["헤지로우, 농림 복합"],
  },
  Germany: {
    species: "가문비나무",
    scientific: "Picea abies",
    carbon_t_co2e_per_year: 0.03,
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Spruce_Forest_Germany.jpg/640px-Spruce_Forest_Germany.jpg",
    description: "독일 산림의 주요 수종 중 하나로 홍수·침식 완화에 기여.",
    env_benefits: ["홍수 완화", "산사태 방지"],
    env_uses: ["산림복원"],
  },
};

// =====================
// 나라별 대표 동식물 (아이콘 + 이름) – 사용자가 원한 형식
// =====================
const COUNTRY_WILDLIFE: Record<string, { icon: JSX.Element; name: string }[]> = {
  "Korea, Republic of": [
    { icon: <Bird className="h-5 w-5" />, name: "참새" },
    { icon: <Bug className="h-5 w-5" />, name: "반딧불이" },
    { icon: <Bird className="h-5 w-5" />, name: "까치" },
  ],
  Japan: [
    { icon: <Bird className="h-5 w-5" />, name: "동박새" },
    { icon: <Bug className="h-5 w-5" />, name: "장수풍뎅이" },
  ],
  China: [
    { icon: <Bird className="h-5 w-5" />, name: "꾀꼬리" },
    { icon: <Fish className="h-5 w-5" />, name: "잉어" },
  ],
  "United States": [
    { icon: <Bird className="h-5 w-5" />, name: "흰머리독수리" },
    { icon: <Bug className="h-5 w-5" />, name: "모나크나비" },
  ],
  Canada: [
    { icon: <Squirrel className="h-5 w-5" />, name: "비버(상징)" },
    { icon: <Bird className="h-5 w-5" />, name: "회색올빼미" },
  ],
  Brazil: [
    { icon: <Bird className="h-5 w-5" />, name: "큰부리새" },
    { icon: <Bug className="h-5 w-5" />, name: "아마존 나비" },
  ],
  Australia: [
    { icon: <Bird className="h-5 w-5" />, name: "코카투" },
    { icon: <Turtle className="h-5 w-5" />, name: "바다거북" },
  ],
  India: [
    { icon: <Bird className="h-5 w-5" />, name: "공작새" },
    { icon: <Bug className="h-5 w-5" />, name: "호랑나비" },
  ],
  Russia: [
    { icon: <Bird className="h-5 w-5" />, name: "수리부엉이" },
    { icon: <Bug className="h-5 w-5" />, name: "딱정벌레" },
  ],
  "South Africa": [
    { icon: <Bird className="h-5 w-5" />, name: "참새사자(팀) – 상징" },
    { icon: <Bug className="h-5 w-5" />, name: "흰개미" },
  ],
  France: [
    { icon: <Bird className="h-5 w-5" />, name: "백조" },
    { icon: <Bug className="h-5 w-5" />, name: "무당벌레" },
  ],
  "United Kingdom": [
    { icon: <Bird className="h-5 w-5" />, name: "송골매" },
    { icon: <Bug className="h-5 w-5" />, name: "붉은여치" },
  ],
  Germany: [
    { icon: <Bird className="h-5 w-5" />, name: "황새" },
    { icon: <Bug className="h-5 w-5" />, name: "쇠똥구리" },
  ],
};

// =====================
// 유틸: Leaflet CSS 주입
// =====================
function useLeafletCss() {
  useEffect(() => {
    const id = "leaflet-css";
    if (!document.getElementById(id)) {
      const link = document.createElement("link");
      link.id = id;
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
  }, []);
}

// 이모지 마커(성장 단계 표시)
const stageEmoji = (s: number) => (s === 0 ? "🌱" : s === 1 ? "🌿" : s === 2 ? "🌳" : "🌲");
const treeIcon = (s: number) =>
  L.divIcon({ html: `<div style="font-size:24px">${stageEmoji(s)}</div>`, className: "", iconSize: [28, 28], iconAnchor: [14, 14] });

// 맵 이동 헬퍼
function FlyTo({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, Math.max(map.getZoom(), 4), { duration: 0.8 });
  }, [center]);
  return null;
}

// =====================
// 메인 앱
// =====================
export default function ForestWorldApp() {
  useLeafletCss();

  const [center, setCenter] = useState<[number, number]>([20, 0]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Tree | null>(null);
  const [trees, setTrees] = useState<Tree[]>([]);
  const [animatingTree, setAnimatingTree] = useState<string | null>(null);
  const [wildlifeCount, setWildlifeCount] = useState<Record<string, number>>({});

  // 출석체크(하루 1회)
  const todayKey = new Date().toISOString().slice(0, 10);
  const [checkedToday, setCheckedToday] = useState<boolean>(() => {
    try {
      return localStorage.getItem("checkin-date") === todayKey;
    } catch {
      return false;
    }
  });
  useEffect(() => {
    try {
      if (checkedToday) localStorage.setItem("checkin-date", todayKey);
    } catch {}
  }, [checkedToday]);

  // 검색 필터
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return trees;
    return trees.filter((t) => [t.name, t.species, t.country, t.scientific ?? ""].some((v) => v.toLowerCase().includes(q)));
  }, [query, trees]);

  // 나라 선택 상태
  const [selectedCountry, setSelectedCountry] = useState<string | undefined>(undefined);

  // 씨앗 심기: 출석 후 원하는 나라에 1그루 생성
  const plantSeed = () => {
    if (!checkedToday || !selectedCountry) return;
    const center = COUNTRY_CENTER[selectedCountry];
    const base = COUNTRY_TREE_INFO[selectedCountry] || {};
    const id = `${selectedCountry}-${Date.now()}`;
    const newTree: Tree = {
      id,
      name: `${selectedCountry} – ${base.species ?? "나무"}`,
      species: base.species ?? "나무",
      scientific: base.scientific,
      country: selectedCountry,
      location: center,
      height_m: base.height_m ?? undefined,
      age_years: base.age_years ?? undefined,
      status: base.status ?? "보전 대상",
      carbon_t_co2e_per_year: base.carbon_t_co2e_per_year ?? 0.02,
      env_benefits: base.env_benefits ?? ["그늘 제공", "탄소흡수"],
      env_uses: base.env_uses ?? ["도시녹화"],
      image: base.image,
      description: base.description,
      source: base.source ?? "Demo dataset",
      lastUpdated: new Date().toISOString().slice(0, 10),
      growthStage: 0,
      morningWatered: false,
      eveningWatered: false,
    };
    setTrees((prev) => [...prev, newTree]);
    setCenter(center);
  };

  // 물/비료 주기 → 아침/저녁 1회씩 채우면 레벨업
  const waterTree = (tree: Tree, type: "morning" | "evening") => {
    setTrees((prev) =>
      prev.map((t) => {
        if (t.id !== tree.id) return t;
        const updated = { ...t };
        if (type === "morning" && !updated.morningWatered) updated.morningWatered = true;
        if (type === "evening" && !updated.eveningWatered) updated.eveningWatered = true;
        if (updated.morningWatered && updated.eveningWatered && updated.growthStage < 3) {
          updated.growthStage += 1;
          updated.morningWatered = false;
          updated.eveningWatered = false;

          // 애니메이션 트리 표시
          setAnimatingTree(updated.id);
          setTimeout(() => setAnimatingTree(null), 1500);

          // 나라별 동식물 1종씩 등장
          const c = updated.country;
          if (COUNTRY_WILDLIFE[c]) {
            setWildlifeCount((prev) => {
              const next = Math.min((prev[c] ?? 0) + 1, COUNTRY_WILDLIFE[c].length);
              return { ...prev, [c]: next };
            });
          }
        }
        return updated;
      })
    );
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden" style={{ backgroundImage: "linear-gradient(180deg, #052e1a 0%, #0b3d26 60%, #0a3220 100%)" }}>
      {/* 헤더 */}
      <div className="absolute inset-x-0 top-0 z-30 flex items-center justify-between p-4 text-white">
        <div className="flex items-center gap-2">
          <Leaf className="h-6 w-6" />
          <h1 className="text-xl md:text-2xl font-semibold">환경을 지키자 🌍 세계 숲 지도</h1>
        </div>
        <div className="flex items-center gap-2">
          <Input placeholder="나무/국가/학명 검색" value={query} onChange={(e) => setQuery(e.target.value)} className="w-44 sm:w-72 bg-white/90" />
        </div>
      </div>

      {/* 좌측 컨트롤 패널 */}
      <div className="absolute left-4 top-20 z-30 w-[300px] space-y-3 rounded-2xl bg-black/40 p-4 text-white backdrop-blur">
        <div className="text-sm font-semibold mb-1">1) 오늘의 출석체크</div>
        <Button variant="secondary" className="w-full" disabled={checkedToday} onClick={() => setCheckedToday(true)}>
          {checkedToday ? "오늘 출석 완료 ✅" : "출석체크 하기"}
        </Button>

        <div className="text-sm font-semibold mt-3">2) 나라 선택 후 씨앗 심기</div>
        <Select value={selectedCountry} onValueChange={(v) => setSelectedCountry(v)}>
          <SelectTrigger className="bg-white/90 text-black">
            <SelectValue placeholder="나라 선택" />
          </SelectTrigger>
          <SelectContent>
            {Object.keys(COUNTRY_CENTER).map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button className="w-full" disabled={!checkedToday || !selectedCountry} onClick={plantSeed}>
          <Sprout className="mr-2 h-4 w-4" /> 씨앗 심기
        </Button>
        <p className="text-[12px] opacity-80">
          출석 후 씨앗을 심고, 상세에서 <span className="font-semibold">아침 물 💧 / 저녁 비료 🌿</span>를 주면 <span className="font-semibold">묘목 → 새싹 → 어린나무 → 큰 나무</span>로 자랍니다.
        </p>

        {/* 나라별 등장한 생물 목록 */}
        <div className="mt-4 rounded-xl bg-white/10 p-3">
          <div className="text-sm font-semibold mb-1">숲에 돌아온 생물들</div>
          <div className="space-y-2 max-h-40 overflow-auto pr-1">
            {Object.keys(wildlifeCount).length === 0 && <div className="text-xs opacity-80">아직 등장한 생물이 없어요.</div>}
            {Object.entries(wildlifeCount).map(([country, count]) => (
              <div key={country}>
                <div className="text-xs mb-1">{country}</div>
                <div className="flex flex-wrap gap-2">
                  {COUNTRY_WILDLIFE[country].slice(0, count).map((w, i) => (
                    <div key={i} className="flex items-center gap-1 rounded-md bg-black/30 px-2 py-1 text-xs">
                      {w.icon}
                      {w.name}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 지도 */}
      <div className="absolute inset-0">
        <MapContainer center={center} zoom={2} minZoom={2} worldCopyJump className="h-full w-full">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
          <FlyTo center={center} />
          {filtered.map((t) => (
            <Marker key={t.id} position={t.location} icon={treeIcon(t.growthStage)} eventHandlers={{ click: () => { setSelected(t); setCenter(t.location); } }}>
              {animatingTree === t.id && (
                <AnimatePresence>
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1.6, opacity: 1 }}
                    exit={{ scale: 1, opacity: 0 }}
                    transition={{ duration: 1 }}
                    className="absolute -top-6 left-1/2 -translate-x-1/2 text-yellow-300"
                  >
                    <Sparkles className="h-6 w-6" />
                  </motion.div>
                </AnimatePresence>
              )}
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* 상세 패널 */}
      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent side="right" className="w-full sm:max-w-lg p-0 overflow-hidden">
          {selected && (
            <div className="flex h-full flex-col">
              <div className="relative h-48 w-full overflow-hidden">
                {selected.image ? (
                  <img src={selected.image} alt={selected.species} className="h-full w-full object-cover" />
                ) : (
                  <div className="h-full w-full bg-emerald-900/30 flex items-center justify-center text-6xl">{stageEmoji(selected.growthStage)}</div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-3 left-3 text-white">
                  <div className="text-lg font-semibold drop-shadow">{selected.name}</div>
                  <div className="text-xs opacity-90">{selected.country}</div>
                </div>
              </div>

              <div className="p-4 space-y-4">
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => waterTree(selected, "morning")} disabled={selected.morningWatered} className="flex items-center gap-1">
                    <Droplets className="h-4 w-4" /> 아침 물주기
                  </Button>
                  <Button variant="outline" onClick={() => waterTree(selected, "evening")} disabled={selected.eveningWatered} className="flex items-center gap-1">
                    <FlaskConical className="h-4 w-4" /> 저녁 비료주기
                  </Button>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Badge className="bg-emerald-600/90 text-white">{selected.species}</Badge>
                  {selected.scientific && <Badge variant="secondary" className="bg-white/70">{selected.scientific}</Badge>}
                  {selected.status && <Badge variant="secondary" className="bg-white/60">{selected.status}</Badge>}
                </div>

                {selected.description && <p className="text-sm leading-relaxed text-neutral-800">{selected.description}</p>}

                {selected.env_benefits && (
                  <div>
                    <h3 className="text-sm font-semibold flex items-center gap-1"><Sprout className="h-4 w-4 text-green-600" /> 환경 기여</h3>
                    <ul className="list-disc pl-5 text-sm text-neutral-700 mt-1 space-y-1">
                      {selected.env_benefits.map((b, i) => (
                        <li key={i}>{b}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selected.env_uses && (
                  <div>
                    <h3 className="text-sm font-semibold flex items-center gap-1"><Leaf className="h-4 w-4 text-emerald-600" /> 활용</h3>
                    <ul className="list-disc pl-5 text-sm text-neutral-700 mt-1 space-y-1">
                      {selected.env_uses.map((u, i) => (
                        <li key={i}>{u}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3">
                  <Stat label="좌표" value={`${selected.location[0].toFixed(3)}, ${selected.location[1].toFixed(3)}`} />
                  {typeof selected.carbon_t_co2e_per_year === "number" && (
                    <Stat label="연간 탄소흡수" value={`${selected.carbon_t_co2e_per_year} tCO₂e`} />
                  )}
                </div>

                <div className="text-xs text-neutral-500 flex justify-between">
                  <div>성장 단계: {selected.growthStage === 0 ? "씨앗" : selected.growthStage === 1 ? "새싹" : selected.growthStage === 2 ? "어린 나무" : "큰 나무"}</div>
                  {selected.lastUpdated && <div>마지막 업데이트: {selected.lastUpdated}</div>}
                </div>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-neutral-50 p-3 shadow-inner">
      <div className="text-[11px] uppercase tracking-wide text-neutral-500">{label}</div>
      <div className="text-base font-semibold">{value}</div>
    </div>
  );
}

