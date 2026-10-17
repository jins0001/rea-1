# 2단계: APK 안의 코드 한 조각을 사람이 읽을 수 있는 Java 코드로 되살리기
# 대상: 앱의 첫 화면(ApiDemos)이 만들어질 때 실행되는 onCreate 함수

. "$PSScriptRoot\00_env.ps1"
$apk = Join-Path $Samples 'ApiDemos-debug.apk'

# 먼저 클래스 안에 어떤 함수들이 있는지 목록 보기
Invoke-Rea -Name '02a_apk_class' -ReaArgs @(
    'inspect-android-class', $apk, 'io.appium.android.apis.ApiDemos'
)

# 그중 onCreate 함수를 Java 코드로 복원
Invoke-Rea -Name '02b_apk_method' -ReaArgs @(
    'inspect-android-method', $apk, 'io.appium.android.apis.ApiDemos', 'onCreate'
)
