import subprocess
from ovos_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler, skill_api_method

class VoiceChangerSkill(OVOSSkill):
    def __init__(self, *args, bus=None, skill_id="", **kwargs):
        super().__init__(*args, bus=bus, skill_id=skill_id, **kwargs)
        self.voice_changer_process = None

    @intent_handler("activate_voice_changer.intent")
    def handle_activate_voice_changer(self, message: Message):
        """
        Handle a request to activate the voice changer.
        """
        if self.voice_changer_process and self.voice_changer_process.poll() is None:
            self.speak_dialog("voice_changer_already_active")
            return

        self.speak_dialog("activating_voice_changer")
        try:
            self.voice_changer_process = subprocess.Popen(
                ["/usr/bin/sox", "--buffer", "2048", "-t", "alsa", "default", "-t", "alsa", "hw:3,0", "noisered", "noise.prof", "0.41", "vol", "0.5", "pitch", "-600", "overdrive", "30", "20", "echo", "0.8", "0.88", "60", "0.4", "chorus", "0.7", "0.9", "55", "0.4", "0.252", "-t", "tremolo", "70", "100", "pitch", "370"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.speak_dialog("voice_changer_activated")
        except Exception as e:
            self.log.error(f"Failed to start voice changer: {e}")
            self.speak_dialog("activation_failed")

    @intent_handler("deactivate_voice_changer.intent")
    def handle_deactivate_voice_changer(self, message: Message):
        """
        Handle a request to deactivate the voice changer.
        """
        if self.voice_changer_process and self.voice_changer_process.poll() is None:
            self.speak_dialog("deactivating_voice_changer")
            self.voice_changer_process.terminate()
            self.voice_changer_process = None
            self.speak_dialog("voice_changer_deactivated")
        else:
            self.speak_dialog("voice_changer_not_active")

    def shutdown(self):
        """
        Ensure the voice changer process is terminated on shutdown.
        """
        if self.voice_changer_process and self.voice_changer_process.poll() is None:
            self.voice_changer_process.terminate()
        super().shutdown()
