import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats

import sys


class PacketDropTestBot(BaseAgent):

	def initialize_agent(self):
		# This runs once before the bot starts up
		self.controllerState = SimpleControllerState()
		
		self.lastTime = 0
		self.realLastTime = 0
		self.doneTicks = 0
		self.skippedTicks = 0
		self.ticksThisPacket = 0
		self.FPS = 120
		self.lastQuickChatTime = 0
		self.secondMessage = None
		self.currentTick = 0
		self.firstTpsReport = True

	def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
		self.packet = packet
		self.handleTime()

		return self.controllerState




	def handleTime(self):
		# this is the most conservative possible approach, but it could lead to having a "backlog" of ticks if seconds_elapsed
		# isnt perfectly accurate.
		if not self.lastTime:
			self.lastTime = self.packet.game_info.seconds_elapsed
		else:
			if self.realLastTime == self.packet.game_info.seconds_elapsed:
				return

			if int(self.lastTime) != int(self.packet.game_info.seconds_elapsed):
				# if self.skippedTicks > 0:
				print(f"did {self.doneTicks}, skipped {self.skippedTicks}")
				if self.firstTpsReport:
					self.firstTpsReport = False
				elif self.doneTicks < 110:
					self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Custom_Excuses_Lag)
				self.skippedTicks = self.doneTicks = 0

			ticksPassed = round(max(1, (self.packet.game_info.seconds_elapsed - self.lastTime) * self.FPS))
			self.lastTime = min(self.packet.game_info.seconds_elapsed, self.lastTime + ticksPassed)
			self.realLastTime = self.packet.game_info.seconds_elapsed
			self.currentTick += ticksPassed
			if ticksPassed > 1:
				# print(f"Skipped {ticksPassed - 1} ticks!")
				self.skippedTicks += ticksPassed - 1
			self.doneTicks += 1