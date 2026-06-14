- name: Save report
  run: |
    mkdir -p reports
    cp report.md reports/$(date +'%Y-%m-%d')_report.md
