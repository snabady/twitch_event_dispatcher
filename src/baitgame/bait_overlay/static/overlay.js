const overlay = document.getElementById("overlay");

// 20 Slots erzeugen
const slots = Array.from({ length: 20 }, () => ({
  busy: false,
  element: null
}));

for (let i = 0; i < 20; i++) {
  const slotEl = document.createElement("div");
  slotEl.classList.add("slot");
  overlay.appendChild(slotEl);
  slots[i].element = slotEl;
}

// SSE-Verbindung
const evtSource = new EventSource("/stream");

evtSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleFishingEvent(data);
};

function handleFishingEvent({ name, result, fishingTime }) {
  // freien Slot finden
  const freeSlots = slots.filter(s => !s.busy);
  if (freeSlots.length === 0) {
    console.warn("Kein freier Slot!");
    return;
  }

  const slot = freeSlots[Math.floor(Math.random() * freeSlots.length)];
  const slotEl = slot.element;
  slot.busy = true;

  // Angelschnur
  const line = document.createElement("div");
  line.classList.add("fishing-line");
  slotEl.appendChild(line);

  setTimeout(() => {
    // nach fishingTime: remove line
    line.remove();

    if (result > -1) {
      const fish = document.createElement("div");
      fish.classList.add("fish");

      const resultLabel = document.createElement("div");
      resultLabel.classList.add("result");
      resultLabel.textContent = `${result}kg`;

      slotEl.appendChild(fish);
      slotEl.appendChild(resultLabel);

      // Fisch 2 Sekunden anzeigen, dann alles entfernen
      setTimeout(() => {
        fish.remove();
        resultLabel.remove();
        slot.busy = false;
      }, 2000);
    } else {
      slot.busy = false;
    }

  }, fishingTime);
}

