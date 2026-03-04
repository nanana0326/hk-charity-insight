"use client";

import dynamic from "next/dynamic";
import type { CSSProperties } from "react";
import type { ChartSpec } from "@/lib/api";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

const defaultStyle: CSSProperties = { height: 320, width: "100%" };

const ORANGE = "#ea580c";
const ORANGE_LIGHT = "#fff7ed";
const GRAY = "#6b7280";
const BORDER = "#e5e7eb";

function buildOption(spec: ChartSpec) {
  const base = {
    title: {
      text: spec.title,
      left: "center",
      textStyle: { color: "#1f2937", fontSize: 14 },
    },
    backgroundColor: "transparent",
  } as const;

  if (spec.type === "pie") {
    const seriesData = (spec.data.series ?? []) as { name: string; value: number }[];
    return {
      ...base,
      color: [ORANGE, "#fb923c", "#fdba74", "#fed7aa"],
      tooltip: { trigger: "item" },
      legend: {
        top: "bottom",
        textStyle: { color: GRAY },
      },
      series: [
        {
          type: "pie",
          radius: ["40%", "70%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: "#fff",
            borderWidth: 2,
          },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 14, fontWeight: "bold" },
          },
          labelLine: { show: false },
          data: seriesData,
        },
      ],
    };
  }

  if (spec.type === "line") {
    const x = (spec.data.x ?? []) as string[];
    const series = (spec.data.series ?? []) as { name: string; data: number[] }[];
    return {
      ...base,
      color: [ORANGE],
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: x,
        axisLabel: { color: GRAY },
        axisLine: { lineStyle: { color: BORDER } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: GRAY },
        splitLine: { lineStyle: { color: BORDER } },
      },
      series: series.map((s) => ({
        type: "line",
        name: s.name,
        data: s.data,
        smooth: true,
        lineStyle: { color: ORANGE },
        itemStyle: { color: ORANGE },
      })),
      legend: {
        top: 24,
        textStyle: { color: GRAY },
      },
    };
  }

  return {
    ...base,
    tooltip: {},
    xAxis: { type: "category" },
    yAxis: { type: "value" },
    series: [],
  };
}

export function BaseChart({ spec }: { spec: ChartSpec }) {
  const option = buildOption(spec);
  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-white p-4 shadow-sm">
      <ReactECharts option={option} style={defaultStyle} />
      {spec.description ? (
        <p className="mt-3 text-xs text-[var(--color-muted)]">{spec.description}</p>
      ) : null}
    </div>
  );
}
