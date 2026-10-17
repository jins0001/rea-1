# 1단계: 안드로이드 앱(APK)의 "신분증" 보기
# 앱 이름, 버전, 필요한 권한, 클래스 개수 등을 JADX로 읽어 옵니다. (앱을 실행하지 않음)

. "$PSScriptRoot\00_env.ps1"
Invoke-Rea -Name '01_apk_overview' -ReaArgs @(
    'inspect-android-package', (Join-Path $Samples 'ApiDemos-debug.apk')
)
