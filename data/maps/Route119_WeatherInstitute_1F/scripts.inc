Route119_WeatherInstitute_1F_MapScripts::
	.byte 0

Route119_WeatherInstitute_1F_EventScript_H0::
	msgbox Route119_WeatherInstitute_1F_Text_H0, MSGBOX_NPC
	end

Route119_WeatherInstitute_1F_EventScript_H1::
	msgbox Route119_WeatherInstitute_1F_Text_H1, MSGBOX_SIGN
	end

Route119_WeatherInstitute_1F_EventScript_H2::
	msgbox Route119_WeatherInstitute_1F_Text_H2, MSGBOX_SIGN
	end

Route119_WeatherInstitute_1F_EventScript_H3::
	msgbox Route119_WeatherInstitute_1F_Text_H3, MSGBOX_SIGN
	end

Route119_WeatherInstitute_1F_EventScript_H4::
	msgbox Route119_WeatherInstitute_1F_Text_H4, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow weather-space v1

Route119_WeatherInstitute_1F_EventScript_Shelter::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_WEATHER_RESCUED, Route119_WeatherInstitute_1F_EventScript_ShelterAfter
 msgbox Route119_WeatherInstitute_1F_Text_ShelterBefore
 release
 end
Route119_WeatherInstitute_1F_EventScript_ShelterAfter::
 msgbox Route119_WeatherInstitute_1F_Text_ShelterAfter
 release
 end
@ END PATCH
