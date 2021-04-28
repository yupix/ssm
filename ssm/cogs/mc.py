import random

from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol


class QuarryProtocol(ServerProtocol):
    def player_joined(self):
        ServerProtocol.player_joined(self)
        secure = random.randint(00000000000, 99999999999)
        self.close(f"§6§l認証コードを発行しました\n§fコード: §7{secure}")


class QuarryFactory(ServerFactory):
    protocol = QuarryProtocol

    motd = "Powered by Quarry!"


def main():
    factory = QuarryFactory()
    factory.listen("")
    reactor.run()


if __name__ == "__main__":
    main()
