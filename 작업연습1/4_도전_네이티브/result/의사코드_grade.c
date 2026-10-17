
undefined1  [16] main_grade(int param_1,int param_2)

{
  undefined *puVar1;
  int iVar2;
  int iVar3;
  int unaff_R14;
  double dVar4;
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  int iStack0000000000000008;
  
  iStack0000000000000008 = param_1;
  while (&stack0x00000000 <= *(undefined1 **)(unaff_R14 + 0x10)) {
    runtime_morestack_noctxt_abi0();
  }
  iVar2 = 0;
  while( true ) {
    if (param_2 <= iVar2) {
      iVar2 = 0;
      for (iVar3 = 0; iVar3 < param_2; iVar3 = iVar3 + 1) {
        iVar2 = iVar2 + *(int *)(iStack0000000000000008 + iVar3 * 8);
      }
      dVar4 = (double)iVar2 / (double)param_2;
      if (dVar4 < 90.0) {
        if (dVar4 < 80.0) {
          if (dVar4 < 70.0) {
            if (dVar4 < 60.0) {
              puVar1 = &DAT_1400b2cc8;
            }
            else {
              puVar1 = &DAT_1400a8002;
            }
          }
          else {
            puVar1 = &DAT_1400a8001;
          }
        }
        else {
          puVar1 = &DAT_1400b2cc0;
        }
      }
      else {
        puVar1 = &DAT_1400a8000;
      }
      iVar2 = 0;
      while( true ) {
        if (param_2 <= iVar2) {
          auVar6 = runtime_concatstring2(0,puVar1,1,&DAT_1400a8003,1);
          return auVar6;
        }
        if (*(int *)(iStack0000000000000008 + iVar2 * 8) < 0x5f) break;
        iVar2 = iVar2 + 1;
      }
      auVar6._8_8_ = 1;
      auVar6._0_8_ = puVar1;
      return auVar6;
    }
    if (*(int *)(iStack0000000000000008 + iVar2 * 8) < 0x28) break;
    iVar2 = iVar2 + 1;
  }
  auVar5._8_8_ = 1;
  auVar5._0_8_ = &DAT_1400b2cc8;
  return auVar5;
}

