from flask_assets import Environment, Bundle

assets = Environment()

assets.register('common_css', Bundle(
        './css/style.css',
        output='./css/common.%(version)s.min.css'))
