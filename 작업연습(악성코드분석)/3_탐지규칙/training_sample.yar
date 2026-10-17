rule Training_Sample_Indicators
{
    meta:
        description = "훈련용 샘플 탐지 규칙 (연습용 초안)"
        sha256 = "0d2e4528b1b151bc45b8fa6e2b35ddc09f3a46d8dbcd47dcb189502025802601"
        date = "2026-10-18"
    strings:
        $s0 = "http://update-check.training.invalid/beacon.php" ascii wide
        $s1 = "Global\\TRAINING_SAMPLE_MUTEX_7F3A" ascii wide
        $s2 = "%APPDATA%\\SysUpdate\\svchost_update.exe" ascii wide
        $s3 = "Mozilla/5.0 (TrainingBot/1.0)" ascii wide
    condition:
        uint16(0) == 0x5A4D and 2 of ($s*)
}
