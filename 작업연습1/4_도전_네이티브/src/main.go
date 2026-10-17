// 성적 계산기 Go 버전 (C# 버전과 같은 규칙)
// 빌드하면 기계어(네이티브) exe가 됩니다 → 분석이 훨씬 어려워지는 것을 비교해 보는 용도
package main

import (
	"fmt"
	"os"
	"strconv"
)

const failLine = 40
const perfectLine = 95

func average(scores []int) float64 {
	sum := 0
	for _, s := range scores {
		sum += s
	}
	return float64(sum) / float64(len(scores))
}

func letterFor(avg float64) string {
	switch {
	case avg >= 90:
		return "A"
	case avg >= 80:
		return "B"
	case avg >= 70:
		return "C"
	case avg >= 60:
		return "D"
	}
	return "F"
}

func grade(scores []int) string {
	for _, s := range scores {
		if s < failLine {
			return "F"
		}
	}
	letter := letterFor(average(scores))
	for _, s := range scores {
		if s < perfectLine {
			return letter
		}
	}
	return letter + "+"
}

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		fmt.Println("usage: gradecalc.exe score1 score2 ...")
		os.Exit(1)
	}
	scores := make([]int, len(args))
	for i, a := range args {
		v, err := strconv.Atoi(a)
		if err != nil || v < 0 || v > 100 {
			fmt.Println("error: scores must be 0-100")
			os.Exit(2)
		}
		scores[i] = v
	}
	fmt.Printf("average=%.1f grade=%s\n", average(scores), grade(scores))
}
