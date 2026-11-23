"""Freeze matched zero-hint comparison manifests for two model configurations."""
import json
from pathlib import Path


def main():
    configurations = {'luna-medium': {'model': 'gpt-6-luna', 'effort': 'medium',
                                       'max_output': 8192, 'rates': [0.1, 0.5]},
                      'terra-medium': {'model': 'gpt-6.1-terra', 'effort': 'medium',
                                        'max_output': 8192, 'rates': [1.0, 5.0]},
                      'sonnet-low': {'model': 'claude-sonnet-5-5', 'effort': 'low',
                                      'max_output': 4096, 'rates': [2, 10]}}
    for label, config in configurations.items():
        for index in range(4):
            source = Path(f'experiments/tier4-zero-confirm-{index}.json')
            manifest = json.loads(source.read_text(encoding='utf-8'))
            manifest.update(name=f'tier4-zero-{label}-{index}', model_config=config,
                            source_manifest=source.name,
                            purpose='matched comparison on the same frozen stories and prompts',
                            analysis_plan={'primary': 'zero-hint accuracy and paired story difference '
                                             'versus Luna low',
                                           'controls': 'one hint, full grammar and English at every stage',
                                           'output_failures': 'missing and invalid answers count wrong; '
                                                              'disclose completion and costs',
                                           'caveat': 'public reused sample; no claim of independent '
                                                     'holdout or universal model ability'})
            Path(f'experiments/tier4-zero-{label}-{index}.json').write_text(
                json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('12 matched manifests, 48 shared stories per configuration')


if __name__ == '__main__':
    main()
