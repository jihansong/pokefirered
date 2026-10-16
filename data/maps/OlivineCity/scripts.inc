OlivineCity_MapScripts::
    .byte 0

OlivineCity_DockWorker::
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineCity_DockWorkerRestored
msgbox OlivineCity_Text_DockWorker, MSGBOX_NPC
    end
OlivineCity_DockWorkerRestored::
    msgbox OlivineCity_Text_DockWorkerRestored, MSGBOX_NPC
    end

OlivineCity_GymGuide::
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineCity_GymGuideRestored
msgbox OlivineCity_Text_GymGuide, MSGBOX_NPC
    end
OlivineCity_GymGuideRestored::
    msgbox OlivineCity_Text_GymGuideRestored, MSGBOX_NPC
    end

OlivineCity_CenterSign::
msgbox OlivineCity_Text_CenterSign, MSGBOX_NPC
    end

OlivineCity_MartSign::
msgbox OlivineCity_Text_MartSign, MSGBOX_NPC
    end

OlivineCity_GymSign::
msgbox OlivineCity_Text_GymSign, MSGBOX_NPC
    end

OlivineCity_LighthouseSign::
msgbox OlivineCity_Text_LighthouseSign, MSGBOX_NPC
    end

OlivineCity_CafeSign::
msgbox OlivineCity_Text_CafeSign, MSGBOX_NPC
    end
