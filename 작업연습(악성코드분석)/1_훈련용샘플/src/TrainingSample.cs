// =====================================================================
//  악성코드 분석 훈련용 샘플 (무해함 / HARMLESS TRAINING SAMPLE)
// ---------------------------------------------------------------------
//  - 실제 악성 행위는 하나도 하지 않습니다. 화면에 안내 문구만 출력합니다.
//  - 악성코드 분석 연습을 위해 "흔적(지표, IOC)"처럼 보이는 글자만 넣었습니다.
//    * 주소: .invalid 도메인(절대 접속 불가), 문서용 예시 IP(203.0.113.x, 198.51.100.x)
//    * 레지스트리 경로·파일 경로·뮤텍스 이름: 글자만 있고 사용하지 않음
//  - 외부 DLL 함수는 "선언"만 하고 한 번도 부르지 않습니다.
//    → 분석에서 "선언(가능성)"과 "실제 호출(행위)"을 구분하는 연습용입니다.
// =====================================================================
using System;
using System.Runtime.InteropServices;

namespace Training
{
    internal static class Indicators
    {
        // 분석 연습용 가짜 지표 (사용하지 않음)
        internal static readonly string[] Items =
        {
            "http://update-check.training.invalid/beacon.php",
            "203.0.113.45",
            "198.51.100.7:8443",
            @"Software\Microsoft\Windows\CurrentVersion\Run",
            @"%APPDATA%\SysUpdate\svchost_update.exe",
            @"Global\TRAINING_SAMPLE_MUTEX_7F3A",
            "VFJBSU5JTkcgU0FNUExFIC0gTk9UIE1BTFdBUkU=",
            "Mozilla/5.0 (TrainingBot/1.0)",
        };
    }

    internal static class NativeDeclarations
    {
        // 선언만 있음 — 어디에서도 호출하지 않음
        [DllImport("kernel32.dll")] internal static extern bool IsDebuggerPresent();
        [DllImport("kernel32.dll")] internal static extern IntPtr VirtualAlloc(IntPtr addr, UIntPtr size, uint type, uint protect);
        [DllImport("wininet.dll")]  internal static extern IntPtr InternetOpenUrlA(IntPtr h, string url, string headers, uint len, uint flags, IntPtr ctx);
        [DllImport("advapi32.dll")] internal static extern int RegSetValueExA(IntPtr key, string name, int reserved, int type, byte[] data, int size);
    }

    public static class Program
    {
        public static int Main()
        {
            Console.WriteLine("HARMLESS TRAINING SAMPLE - for malware analysis practice only.");
            Console.WriteLine("This program performs no network, registry, file, or memory actions.");
            Console.WriteLine("Embedded indicator strings: " + Indicators.Items.Length);
            return 0;
        }
    }
}
