from flask_assets import Environment, Bundle

assets = Environment()

# CSS Assets

assets.register('common_css', Bundle(
        './css/style.css',
        output='./css/common.%(version)s.css'))

# Javascript Assets

assets.register('profile_js', Bundle(
        './js/profile.js',
        output='./js/profile.%(version)s.min.js'
))