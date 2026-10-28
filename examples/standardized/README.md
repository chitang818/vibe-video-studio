# 标准组件的受控正例

输入由 make_fixture.py 生成，配音是明确的合成测试音，不是真人口播。用于检查组件、时间戳、排版和工程协议，不能作为科学/听感已验收成品。

```powershell
python examples/standardized/make_fixture.py --out artifacts/component-demo-input
python vibe.py compile --story artifacts/component-demo-input/story.json --voice artifacts/component-demo-input/voice.wav --timestamps artifacts/component-demo-input/timestamps.json --script artifacts/component-demo-input/script.txt --caption-groups artifacts/component-demo-input/captions.json --out artifacts/component-demo-project
python vibe.py audit artifacts/component-demo-project
```

输出是待复核草稿；不存在预填的正式审核签名。重复演示时使用新的目录名。
