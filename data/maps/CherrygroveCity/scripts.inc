CherrygroveCity_MapScripts::
    .byte 0


CherrygroveCity_Guide::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MET_LAB_ASSISTANT, CherrygroveCity_GuideBeforeLab
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, CherrygroveCity_GuideReportDone
    goto_if_set FLAG_JOHTO_MET_CHERRYGROVE_GUIDE, CherrygroveCity_GuideAgain
    msgbox CherrygroveCity_Text_GuideRequest
    setflag FLAG_JOHTO_MET_CHERRYGROVE_GUIDE
    release
    end
CherrygroveCity_GuideBeforeLab::
    msgbox CherrygroveCity_Text_GuideBeforeLab
    release
    end
CherrygroveCity_GuideAgain::
    msgbox CherrygroveCity_Text_GuideAgain
    release
    end
CherrygroveCity_GuideReportDone::
    msgbox CherrygroveCity_Text_GuideReportDone
    release
    end

CherrygroveCity_Girl::
    msgbox CherrygroveCity_Text_Girl, MSGBOX_NPC
    end

CherrygroveCity_Fisher::
    msgbox CherrygroveCity_Text_Fisher, MSGBOX_NPC
    end

CherrygroveCity_CenterSign::
    msgbox CherrygroveCity_Text_CenterSign, MSGBOX_NPC
    end

CherrygroveCity_MartSign::
    msgbox CherrygroveCity_Text_MartSign, MSGBOX_NPC
    end

CherrygroveCity_GuideSign::
    msgbox CherrygroveCity_Text_GuideSign, MSGBOX_NPC
    end
