// 성적 계산기 (연습용 원본 프로그램)
// 사용법: GradeCalc.exe 점수1 점수2 점수3 ...
// 예)    GradeCalc.exe 90 85 77
//
// 숨은 규칙(분석으로 찾아낼 것):
//   1) 평균에 따라 A/B/C/D/F 등급
//   2) 한 과목이라도 40점 미만이면 평균과 상관없이 F (과락)
//   3) 모든 과목이 95점 이상이면 등급 뒤에 "+" (만점 보너스)
using System;

namespace PracticeApp
{
    public static class GradeRules
    {
        public const int FailLine = 40;
        public const int PerfectLine = 95;

        public static double Average(int[] scores)
        {
            int sum = 0;
            foreach (int s in scores)
            {
                sum += s;
            }
            return (double)sum / scores.Length;
        }

        public static string LetterFor(double average)
        {
            if (average >= 90) return "A";
            if (average >= 80) return "B";
            if (average >= 70) return "C";
            if (average >= 60) return "D";
            return "F";
        }

        public static string Grade(int[] scores)
        {
            foreach (int s in scores)
            {
                if (s < FailLine) return "F";
            }

            string letter = LetterFor(Average(scores));

            bool perfect = true;
            foreach (int s in scores)
            {
                if (s < PerfectLine) perfect = false;
            }
            return perfect ? letter + "+" : letter;
        }
    }

    public static class Program
    {
        public static int Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("usage: GradeCalc.exe score1 score2 ...");
                return 1;
            }

            int[] scores = new int[args.Length];
            for (int i = 0; i < args.Length; i++)
            {
                int value;
                if (!int.TryParse(args[i], out value) || value < 0 || value > 100)
                {
                    Console.WriteLine("error: scores must be 0-100");
                    return 2;
                }
                scores[i] = value;
            }

            Console.WriteLine(string.Format("average={0:F1} grade={1}",
                GradeRules.Average(scores), GradeRules.Grade(scores)));
            return 0;
        }
    }
}
