from StringIO import StringIO
from zipfile import ZipFile

YIFY_DL_BASE = 'http://www.yifysubtitles.com/subtitle/'
YIFY_SUBS_BASE = 'http://www.yifysubtitles.com/movie-imdb/%s'

####################################################################################################
class YifyMoviesSubtitles(Agent.Movies):

	name = 'YIFY Movies Subtitles'
	languages = [Locale.Language.NoLanguage]
	primary_provider = False
	contributes_to = ['com.plexapp.agents.imdb']

	def search(self, results, media, lang):
		results.Append(MetadataSearchResult(id = media.primary_metadata.id, score = 100))

	def update(self, metadata, media, lang):
		for i in media.items:
			for part in i.parts:
				fetch_subtitles(part, metadata.id)

####################################################################################################
def fetch_subtitles(part, imdb_id):

	# Get agent preferences
	prefs_languages = list(set([Prefs['lang_1'], Prefs['lang_2'], Prefs['lang_3']]))

	# Remove any posible duplicates from agent preferences
	if 'None' in prefs_languages:
		prefs_languages.remove('None')

	# Get ISO codes for agent preferences languages
	prefs_languages_iso = [get_iso_code(pref_language) for pref_language in prefs_languages]
	
	# Remove all subtitles from languages no longer set in agent preferences
	for subtitle in part.subtitles:
		if subtitle not in prefs_languages_iso:
			part.subtitles[subtitle].validate_keys([])

	# Get languages available to download from yifysubtitles.com
	yifysubtitles_request = HTML.ElementFromURL(YIFY_SUBS_BASE % (imdb_id), sleep=2.0)
	yifysubtitles_available_languages = list(set(yifysubtitles_request.xpath('//tr/td[@class="flag-cell"]/span[@class="sub-lang"]/text()')))

	for pref_language in prefs_languages:
		if pref_language in yifysubtitles_available_languages:
			subtitle_max_rating = str(max(list(map(int, yifysubtitles_request.xpath('//tr[td[@class="flag-cell"]/span[@class="sub-lang"]/text() = "' + pref_language + '"]/td[@class="rating-cell"]/span[1]/text()')))))
			subtitle_relative_path = yifysubtitles_request.xpath('//tr[td[@class="rating-cell"]/span[1]/text() = "' + subtitle_max_rating + '" and td[@class="flag-cell"]/span[@class="sub-lang"]/text() = "' + pref_language + '"]/td[not(@class)]/a/@href')[0]				
			subtitle_download_link = YIFY_DL_BASE + subtitle_relative_path.split('/')[2] + '.zip'
			subtitle_filename = subtitle_download_link.split('/')[-1]

			# Download subtitle only if it's not already present
			if subtitle_filename not in part.subtitles[get_iso_code(pref_language)]:

				# Cleanup other subtitles previously downloaded with this agent, only one subtitle per language is needed
				part.subtitles[get_iso_code(pref_language)].validate_keys([])

				# Unzip file and get subtitle data
				subtitle_zip_file = ZipFile(StringIO(HTTP.Request(subtitle_download_link).content))
				subtitle_data = subtitle_zip_file.open(subtitle_zip_file.namelist()[0]).read()

				# Saving subtitle data to Plex Media Metadata
				part.subtitles[get_iso_code(pref_language)][subtitle_filename] = Proxy.Media(subtitle_data, ext='srt')

			else:
				Log('Skipping, subtitle already downloaded: %s' % (subtitle_download_link))
		else:
			Log('No subtitles available for language "%s"' % (pref_language))
			return None

####################################################################################################
def get_iso_code(language):

	languages = {
		'Albanian': 'sq',
		'Arabic': 'ar',
		'Bengali': 'bn',
		'Brazilian-Portuguese': 'pt-br',
		'Bulgarian': 'bg',
		'Bosnian': 'bs',
		'Chinese': 'zh',
		'Croatian': 'hr',
		'Czech': 'cs',
		'Danish': 'da',
		'Dutch': 'nl',
		'English': 'en',
		'Estonian': 'et',
		'Farsi/Persian': 'fa',
		'Finnish': 'fi',
		'French': 'fr',
		'German': 'de',
		'Greek': 'el',
		'Hebrew': 'he',
		'Hungarian': 'hu',
		'Indonesian': 'id',
		'Italian': 'it',
		'Japanese': 'ja',
		'Korean': 'ko',
		'Lithuanian': 'lt',
		'Macedonian': 'mk',
		'Malay': 'ms',
		'Norwegian': 'no',
		'Polish': 'pl',
		'Portuguese': 'pt',
		'Romanian': 'ro',
		'Russian': 'ru',
		'Serbian': 'sr',
		'Slovenian': 'sl',
		'Spanish': 'es',
		'Swedish': 'sv',
		'Thai': 'th',
		'Turkish': 'tr',
		'Urdu': 'ur',
		'Ukrainian': 'uk',
		'Vietnamese': 'vi'
	}

	if language in languages:
		return languages[language]
####################################################################################################