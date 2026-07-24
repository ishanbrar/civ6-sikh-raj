local SIKH_CIVILIZATION = "CIVILIZATION_SIKH_EMPIRE";
local PERSIA_MUSIC_SWITCH = 1832345227;

local function IsLocalSikhPlayer()
  local localPlayerID = Game.GetLocalPlayer();
  if localPlayerID == nil or localPlayerID < 0 then
    return false;
  end

  local playerConfig = PlayerConfigurations[localPlayerID];
  return playerConfig ~= nil and playerConfig:GetCivilizationTypeName() == SIKH_CIVILIZATION;
end

local function ApplyPersiaMusicSwitch()
  if not IsLocalSikhPlayer() then
    return;
  end

  UI.SetSoundSwitchValue("Game_Location", PERSIA_MUSIC_SWITCH);
  UI.SetSoundSwitchValue("Civilization", PERSIA_MUSIC_SWITCH);
  UI.SetSoundSwitchValue("Leader_Screen_Civilization", PERSIA_MUSIC_SWITCH);
end

Events.LoadGameViewStateDone.Add(ApplyPersiaMusicSwitch);
Events.LoadScreenClose.Add(ApplyPersiaMusicSwitch);
Events.LocalPlayerTurnBegin.Add(ApplyPersiaMusicSwitch);
Events.LocalPlayerChanged.Add(ApplyPersiaMusicSwitch);

ApplyPersiaMusicSwitch();
