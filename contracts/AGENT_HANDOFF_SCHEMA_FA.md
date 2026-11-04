# قرارداد تحویل بین ایجنت‌ها (Agent Handoff)

نسخه: 1.0-draft.

## 1. ساختار الزامی

نمونه JSON نمایشی:

    {
      "task_id": "BOOT-001",
      "agent_id": "AGENT_01",
      "experiment_id": "W0-BASELINE-FREEZE",
      "status": "COMPLETE",
      "objective": "ثبت هویت و نسخه مرجع W0",
      "summary": "هویت فایل، Expert، EA_Version و تنظیمات تطبیق داده شد.",
      "inputs": [
        {
          "artifact": "src/example.mq5",
          "version": "git-commit-or-sha256",
          "role": "source"
        }
      ],
      "outputs": [
        {
          "artifact": "reports/baseline_manifest.json",
          "version": "sha256",
          "role": "baseline_manifest"
        }
      ],
      "code_commit": "commit-sha",
      "data_hash": "data-manifest-hash",
      "config_hash": "config-hash",
      "model_hash": null,
      "checks_run": [
        {
          "check_id": "IDENTITY-CHECK",
          "status": "PASS",
          "evidence": "reports/identity_check.md"
        }
      ],
      "limitations": [],
      "open_findings": [],
      "next_action": "اجرای Gate کامپایل پس از آماده‌شدن محیط MT5",
      "requested_gate": "GATE_1"
    }

نمونه فقط قالب است؛ مقادیر واقعی باید از خروجی همان Task پر شوند.

## 2. فیلدهای مجاز status
- PLANNED: هنوز آغاز نشده.
- IN_PROGRESS: در حال اجرا.
- COMPLETE: خروجی و تست‌های موردنیاز تکمیل شده‌اند.
- BLOCKED: وابستگی یا دسترسی موجود نیست.
- FAILED: اجرا انجام شده اما معیار پذیرش رد شده است.
- INVALIDATED: نتیجه به علت نقض پروتکل/تغییر ورودی قابل استفاده نیست.

## 3. قواعد
1. COMPLETE بدون artifact و شواهد تست معتبر نیست.
2. BLOCKED با FAILED یکسان نیست.
3. هش نامعلوم را جعل نکن؛ null یا NOT_AVAILABLE ثبت کن.
4. ادعای Compile باید به لاگ MetaEditor و build مشخص متصل باشد.
5. ادعای Backtest باید به Expert name، EA_Version، SET، بازه، data model، Journal، HTML و CSV متصل باشد.
6. خروجی مدل باید به Fold، data hash، feature/label schema و training config متصل باشد.
7. تحویل‌دهنده نتیجه ممیزی نهایی خودش را صادر نمی‌کند.
8. درخواست عبور Gate، مجوز خودکار merge یا معامله زنده نیست.
