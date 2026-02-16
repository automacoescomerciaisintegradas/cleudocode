#!/usr/bin/env python3
# AIDEV-NOTE: Monitor de consumo de tokens por provedor de API
import os, json, logging
from datetime import date

logger = logging.getLogger(__name__)
MONITOR_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'token_usage.json')

class TokenMonitor:
    def __init__(self):
        self._usage = self._load()

    def _load(self):
        try:
            if os.path.exists(MONITOR_FILE):
                with open(MONITOR_FILE, 'r') as f:
                    data = json.load(f)
                if data.get('date') != str(date.today()):
                    return self._new_day()
                return data
        except Exception:
            pass
        return self._new_day()

    def _new_day(self):
        return {'date': str(date.today()), 'providers': {}, 'total_requests': 0, 'total_input_tokens': 0, 'total_output_tokens': 0, 'quota_exhausted': []}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(MONITOR_FILE), exist_ok=True)
            with open(MONITOR_FILE, 'w') as f:
                json.dump(self._usage, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f'Erro ao salvar monitor: {e}')

    def register_request(self, provider, model, input_tokens=0, output_tokens=0, success=True, error_type=None):
        if provider not in self._usage['providers']:
            self._usage['providers'][provider] = {'requests': 0, 'success': 0, 'failures': 0, 'input_tokens': 0, 'output_tokens': 0, 'models_used': [], 'last_error': None, 'quota_exhausted': False}
        p = self._usage['providers'][provider]
        p['requests'] += 1
        self._usage['total_requests'] += 1
        if success:
            p['success'] += 1
            p['input_tokens'] += input_tokens
            p['output_tokens'] += output_tokens
            self._usage['total_input_tokens'] += input_tokens
            self._usage['total_output_tokens'] += output_tokens
            if model and model not in p['models_used']:
                p['models_used'].append(model)
        else:
            p['failures'] += 1
            p['last_error'] = error_type
            if error_type == 'quota_exhausted':
                p['quota_exhausted'] = True
                if provider not in self._usage['quota_exhausted']:
                    self._usage['quota_exhausted'].append(provider)
        self._save()

    def is_quota_exhausted(self, provider):
        return self._usage.get('providers', {}).get(provider, {}).get('quota_exhausted', False)

    def get_friendly_error(self, provider, error):
        e = str(error).lower()
        if '429' in e or 'quota' in e or 'rate_limit' in e or 'resource_exhausted' in e:
            self.register_request(provider, None, success=False, error_type='quota_exhausted')
            return '
  ⚠️  Cota diaria do provedor [' + provider + '] esgotada!
  💡 Dica: Gere uma nova chave em https://aistudio.google.com/apikey
  🔄 Tentando proximo provedor...
'
        elif 'not configured' in e or 'nao configurada' in e:
            return None
        elif '401' in e or 'api key not valid' in e:
            self.register_request(provider, None, success=False, error_type='invalid_key')
            return '
  🔑 Chave API invalida para [' + provider + ']. Atualize no .env
'
        elif 'timeout' in e or 'timed out' in e:
            self.register_request(provider, None, success=False, error_type='timeout')
            return '
  ⏱️  Timeout no [' + provider + ']. Servidor offline.
'
        elif '400' in e or 'invalid' in e:
            self.register_request(provider, None, success=False, error_type='bad_request')
            return '
  ⚠️  Erro de config no [' + provider + ']. Checar modelo/chave.
'
        else:
            self.register_request(provider, None, success=False, error_type='unknown')
            return '
  ❌ Erro no [' + provider + ']
'

    def get_summary(self):
        u = self._usage
        lines = ['', '  📊 CONSUMO DE TOKENS — ' + u['date'], '  ' + '='*45]
        lines.append('  Total: ' + str(u['total_requests']) + ' req | In: ' + str(u['total_input_tokens']) + ' | Out: ' + str(u['total_output_tokens']))
        lines.append('  ' + '-'*45)
        for name, p in u.get('providers', {}).items():
            st = '🔴 ESGOTADO' if p.get('quota_exhausted') else '🟢 OK'
            lines.append('  ' + name + ': ' + st + ' | ' + str(p['success']) + '/' + str(p['requests']) + ' ok')
        if u.get('quota_exhausted'):
            lines.append('
  ⚠️  Esgotados: ' + ', '.join(u['quota_exhausted']))
        lines.append('  ' + '='*45 + '
')
        return '
'.join(lines)

token_monitor = TokenMonitor()
