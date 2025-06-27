import asyncio
import aiofiles
import re
from jinja2 import Template

class TemplateManager:
    # TODO ENV
    TEMPLATE_PATH = "/home/snafu/src/twitch-irc/curses/test.txt"
    OUTPUT_PATH = "/home/snafu/src/twitch-irc/curses/test.txt"

    def __init__(self):
        # Standardwerte
        self.bait_name = "test"
        self.weight = 69
        self.last_follower = "deltacore"
        self.last_subscriber = "Legomen68"

    async def load_existing_values(self):
        """Lädt bestehende Werte aus der Datei, falls sie existiert."""
        try:
            async with aiofiles.open(self.OUTPUT_PATH, mode='r', encoding='utf-8') as file:
                content = await file.read()
                #print("Loaded content:", repr(content))  

        except FileNotFoundError:
            logger.debug("File not found, using default values.")
            pass        

    async def load_existing_valuesxx(self):
        
        try:
            async with aiofiles.open(self.OUTPUT_PATH, mode='r', encoding='utf-8') as file:
                content = await file.read()
                #print("Loaded content:", content)

            # Werte aus der bestehenden Datei extrahieren
            bait_match = re.search(r'TOP ! bait: (.+)', content)
            weight_match = re.search(r'with (\d+) g', content)
            follower_match = re.search(r'last Follow, thank u\s+(.+)', content)
            sub_match = re.search(r'Last Sub, thank you\s+(.+)', content)



            #print (f'bait_match {bait_match} .. weight {weight_match}')
            # Falls Werte gefunden wurden, speichern
            #print("blub: ",bait_match.group(1))
            if bait_match: self.bait_name = bait_match.groupdict(bait_match)
            if weight_match: self.weight = int(weight_match.group(1))
            if follower_match: self.last_follower = follower_match.group(1)
            if sub_match: self.last_subscriber = sub_match.group(1)

        except FileNotFoundError:
            # Falls die Datei noch nicht existiert, wird einfach die Standardkonfiguration genutzt
            #print("File not found, using default values.")
            pass

    async def load_existing_valuesx(self):
        """Lädt bestehende Werte aus der Datei, falls sie existiert."""
        try:
            async with aiofiles.open(self.OUTPUT_PATH, mode='r', encoding='utf-8') as file:
                content = await file.read()
            
            #   print("Loaded content:", repr(content))  # Gibt den Inhalt mit unsichtbaren Zeichen aus

            # Werte aus der bestehenden Datei extrahieren
            bait_match = re.search(r'TOP ! bait: (.+)', content)
            if bait_match:
            #    print("Bait Match:", bait_match.group(1))  # Ausgabe der gefundenen Gruppe
                self.bait_name = bait_match.group(1)
            
            # Hier einen zusätzlichen regulären Ausdruck einfügen, um den 'weight' zu extrahieren
            weight_match = re.search(r'with (\d+) g', content)
            if weight_match:
                #print("Weight Match:", weight_match.group(1))  # Ausgabe des gefundenen Werts
                self.weight = int(weight_match.group(1))
            
                #print("Kein Match für das Gewicht gefunden.")
            
            # Weitere extrahieren, wie Follower und Subscriber...
            follower_match = re.search(r'last Follow, thank u \s*(.*)', content)
            if follower_match:
                #print("Follower Match:", follower_match.group(1))  # Ausgabe des gefundenen Werts
                self.last_follower = follower_match.group(1)

            sub_match = re.search(r'Last Sub, thank you\s*(.*)', content)
            if sub_match:
                #print("Subscriber Match:", sub_match.group(1))  # Ausgabe des gefundenen Werts
                self.last_subscriber = sub_match.group(1)

        except FileNotFoundError:
            logger.debug("File not found, using default values.")
            pass


    def set_bait(self, name, weight):
        """Setzt den Bait-Namen und das Gewicht."""
        self.bait_name = name
        self.weight = weight

    def set_follower(self, name):
        """Setzt den letzten Follower."""
        self.last_follower = name

    def set_subscriber(self, name):
        """Setzt den letzten Subscriber."""
        self.last_subscriber = name

    async def generate_filex(self):
        """Generiert die Datei mit den aktuellen Werten."""
        await self.load_existing_values()  # Vorhandene Werte laden

        # Debugging-Ausgabe vor der Dateigenerierung
        logger.debug(f"Generating file with values: Bait={self.bait_name}, Weight={self.weight}, Follower={self.last_follower}, Subscriber={self.last_subscriber}")

        async with aiofiles.open(self.TEMPLATE_PATH, mode='r', encoding='utf-8') as file:
            template_content = await file.read()

        # Jinja2 Template mit den Variablen rendern
        template = Template(template_content)
        new_content = template.render(
            bait_name=self.bait_name,
            weight=self.weight,
            last_follower=self.last_follower,
            last_subscriber=self.last_subscriber
        )

    async def generate_file(self):
        """Generiert die Datei mit den aktuellen Werten."""
        await self.load_existing_values()  # Vorhandene Werte laden

        # Template laden
        async with aiofiles.open(self.TEMPLATE_PATH, mode='r', encoding='utf-8') as file:
            template_content = await file.read()

        template = Template(template_content)

        # Rendering des Templates mit den aktuellen Werten
        new_content = template.render(
            bait_name=self.bait_name,
            weight=self.weight,
            last_follower=self.last_follower,
            last_subscriber=self.last_subscriber
        )

        #print(f"Generating file with values: Bait={self.bait_name}, Weight={self.weight}, Follower={self.last_follower}, Subscriber={self.last_subscriber}")

        # Neues File mit den aktualisierten Werten erstellen
        async with aiofiles.open(self.OUTPUT_PATH, mode='w', encoding='utf-8') as file:
            await file.write(new_content)


        async with aiofiles.open(self.OUTPUT_PATH, mode='w', encoding='utf-8') as file:
            await file.write(new_content)


    async def load_existing_values2(self):
        """Lädt bestehende Werte aus der Datei, falls sie existiert."""
        try:
            async with aiofiles.open(self.OUTPUT_PATH, mode='r', encoding='utf-8') as file:
                content = await file.read()
                #print("Loaded content:", repr(content))  # Gibt den Inhalt mit unsichtbaren Zeichen aus

            # Werte aus der bestehenden Datei extrahieren
            bait_match = re.search(r'TOP ! bait: (.+)', content)
            if bait_match:
                #print("Bait Match:", bait_match.group(1))  # Ausgabe der gefundenen Gruppe
                self.bait_name = bait_match.group(1)
        

        except FileNotFoundError:
            logger.debug("File not found, using default values.")
            pass


# ------------------ TEST ------------------
async def main():
    manager = TemplateManager()
    
    # Bisherige Werte laden
   #await manager.load_existing_values()
    await manager.load_existing_values2()

    # Nur den Bait ändern
    manager.set_bait("sna", 500)
    await manager.generate_file()

    # Nur den letzten Follower ändern
    manager.set_follower("NewFollower_XYZ")
    await manager.generate_file()

    # Nur den letzten Subscriber ändern
    #manager.set_subscriber("UltimateSubscriber123")
    #await manager.generate_file()

#asyncio.run(main())
template_manager = TemplateManager()