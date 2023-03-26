GAME_FPS = 0
MAIN = 0

NAME = 'Embroidery Sketches Printer'
AUTHOR = 'NoneType4Name'
TELEGRAM = f'https://t.me/{AUTHOR}'
GITHUB = 'https://github.com'
RAW_GITHUB = 'https://raw.githubusercontent.com'
API_GITHUB = 'https://api.github.com'
GITHUB_OAUTH_KEY = 'e3d681863cc9855c2b25bb9942faa0e2d12dffff'

DATAS_FOLDER_NAME = 'assets'

NAME_PRINT_PROCESS = 'Embroidery Sketches'
DUMMY_MONITOR = 'monitorHDC'
SKETCHES = 6

HORZRES = 8
VERTRES = 10
LOGPIXELSX = 88
LOGPIXELSY = 90
PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111
PHYSICALOFFSETX = 112
PHYSICALOFFSETY = 113

FONT_PATH = f'{DATAS_FOLDER_NAME}/font.ttf'
SKETCHES_FONT_K = 4
SKETCHES_ELEMENTS_FONT_K = 100
GLUE_PADDING = 3
DEFAULT_SKETCHES_PADDING = 1
TRANSLATE = {
    'Update':{
        'Actual': 'Актуальная версия',
        'ActualButton': 'Проверить',
        'Getting': 'Получение обновлений',
        'GettingButton': '',
        'Loading': 'Загрузка обновления',
        'LoadingButton': '',
        'Available': 'Доступно обновление',
        'AvailableButton': 'Установить',
        'Open': 'Открыть обновление',
        'OpenButton': 'Открыть',
        'Launching': 'Запуск',
        'LaunchingButton': '',
        'LaunchingError': 'Произошла ошибка {}',
    },
    'Sketch':{
        'LeftUp': 'Левый верхний угол',
        'ListNum': 'Лист номер %s',
        'MoreInfo': 'licenced by MIT licence; connect with me: telegram (t.me/NoneType4Name); size:{w}x{h}, dpi:{d}, funcWorkTime: {m}ms.    Удалить это поле перед склеиванием',
        'Author': 'Powered by NoneType4Name.',
        'HeaderInfo': '← Удалить это серое поле и приклеить вниз листа %s →',
        'FooterInfo': '← Место поклейки листа номер %s (поле должно быть скрыто)→',
        'LastInfo': 'Лист номер {} клеится справа от листа {}',
    },
    'About': '{v}, {s}x{d}, dev: '+AUTHOR+', links:',
    'Telegram': 'Telegram',
    'Github': 'GitHub',

    'ButtonPrintEmbroidery': 'Печать выкройки',
    'DescriptionPrintEmbroidery': 'Печать заготовок',
    'Print':{
        'PrinterLabel': 'Принтер',
        'PrinterSelect': '{}',
        'MonochromePrint': 'Монохромная печать',
        'ColoredPrint': 'Цветная печать',
        'ListCounts': 'К печати {count} лист{w} {type}',
        'PrinterIsNotPhysic': 'Принтер не является физическим',
        'BuildSketches': 'Построение чертежа...',
        'BuildUnexpectedErrorDescription': None,
        'BuildUnexpectedError': 'Произошла непредвиденная ошибка\nОткрыть дополонительную информацию?',
        'Settings': 'Вручную',
        'SettingsCaption': '',
        'Start': 'Печать',
        'Exit': 'Отмена',
        'MetricsUnit': 'мм',
        'FuncNames':{1:'FirstElement', 2:'SecondElement', 3:'ThirdElement', 4:'FourthElement', 5:'FifthElement', 6:'SixthElement'},
        'BuildErrorDescription':'Ошибка построения по меркам',
        'BuildErrorText':'Ошибка построения элемента {n}.\n\nКод ошибки: {c}',
        'UnexpectedError':'Произошла непредвиденная ошибка',
    },
    'DefaultMetrics': {
        'Основание груди': '760',
        'Обхват талии': '640',
        'Обхват низа корсета': '840',
        'Высота основания груди': '120',
        # 'Высота бока вверх': '220',
        'Высота бока вниз': '120',
        'Утяжка': '50'
    },
    'AllowedElements': ['Все', 'Элемент {}']


}

COLORS = {
    'background': (200, 200, 200),
    'DataPanel':{
        'background': (100, 200, 200),
        'border': (255, 255, 255),
        'label':{
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (255, 255, 255),
            'textActive': (255, 255, 255),
            'border': (),
            'borderActive': ()
        },
        'textInput':{
            'background': (255, 255, 255),
            'backgroundActive': (202, 219, 252),
            'text': (0, 0, 0),
            'textActive': (0, 0, 0),
            'border': (102, 153, 255),
            'borderActive': (0, 0, 255)
        },
        'switch':{
            'background': (255, 255, 255),
            'backgroundActive': (202, 219, 252),
            'on': (255, 255, 255),
            'off': (100, 200, 200)
        }
    },
    'button': {
        'background': (255, 255, 255),
        'backgroundActive': (202, 219, 252),
        'text': (0, 0, 0),
        'textActive': (0, 0, 0),
        'border': (102, 153, 255),
        'borderActive': (0, 0, 255),
    },
    'PrintWindow':{
        'switch': {
            'background': (255, 255, 255),
            'backgroundActive': (202, 219, 252),
            'on': (255, 255, 255),
            'off': (100, 200, 200)
        },
        'label':{
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (255, 255, 255),
            'textOn': (148, 255, 151),
            'textOff': (255, 255, 255),
            'textActive': (255, 255, 255),
            'textOnActive': (148, 255, 151),
            'textOffActive': (255, 255, 255),
            'border': (),
            'borderActive': (),
            'printerName':{
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
        },
        'button':{
            'close':{
                'background': (255, 0, 0),
                'backgroundActive': (255, 0, 0),
                'text': (255, 255, 255),
                'textActive': (255, 255, 255)
            },
            'down':{
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
            'up':{
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
            'settings': {
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
            'cancel':{
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
            'print': {
                'background': (255, 255, 255),
                'backgroundActive': (202, 219, 252),
                'text': (0, 0, 0),
                'textActive': (0, 0, 0),
                'border': (102, 153, 255),
                'borderActive': (102, 153, 255)
            },
        },
        'description': (255, 255, 255),
        'descriptionBackground': (100, 100, 100),
        'background': (100, 200, 200),
        'backgroundActive': (100, 200, 200),
        'border': (100, 100, 100),
    },
    'label':{
        'About':{
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (255, 255, 255),
            'textActive': (255, 255, 255),
            'border': (),
            'borderActive': ()
            },
        'Git': {
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (87, 96, 106),
            'textActive': (87, 96, 106),
            'border': (),
            'borderActive': ()
        },
        'Tg': {
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (28, 147, 227),
            'textActive': (28, 147, 227),
            'border': (),
            'borderActive': ()
        },
        'UpdateStatus': {
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (255, 255, 255),
            'textActive': (0, 255, 0),
            'border': (),
            'borderActive': (),
            'check':{
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (255, 255, 255),
                'textActive': (255, 255, 0),
                'border': (),
                'borderActive': (),
            },
            'load': {
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (255, 255, 255),
                'textActive': (255, 255, 255),
                'border': (),
                'borderActive': (),
            },
            'available': {
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (255, 0, 0),
                'textActive': (255, 0, 0),
                'border': (),
                'borderActive': (),
            },
            'install': {
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (0, 200, 200),
                'textActive': (0, 200, 200),
                'border': (),
                'borderActive': (),
            },
            'open': {
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (0, 255, 0),
                'textActive': (0, 255, 0),
                'border': (),
                'borderActive': (),
            },
            'error': {
                'background': (0, 0, 0, 0),
                'backgroundActive': (0, 0, 0, 0),
                'text': (255, 0, 0),
                'textActive': (255, 0, 0),
                'border': (),
                'borderActive': (),
            },
        },
        'UpdateButton': {
            'background': (0, 0, 0, 0),
            'backgroundActive': (0, 0, 0, 0),
            'text': (0, 255, 0),
            'textActive': (0, 255, 0),
            'border': (),
            'borderActive': ()
        },
    },
}
