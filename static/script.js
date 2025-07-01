let gameId = window.location.pathname.split("/")[1];
let playerId = null;
let playerName = null;
let updatePlayersInterval = null;
let updateResultInterval = null;
let assignedTargets = new Set();

function getPlayerIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("player_id");
}

async function fetchOwnName() {
  const res = await fetch(`/${gameId}/players`);
  const players = await res.json();
  if (playerId && players[playerId]) {
    return players[playerId];
  }
  return null;
}

function showInviteLink() {
  let invite = document.getElementById("invite-link");
  if (!invite) {
    invite = document.createElement("div");
    invite.id = "invite-link";
    invite.className = "flex flex-col items-center mt-4 mb-2";
    document.querySelector(".bg-white").insertBefore(invite, document.querySelector("#setup").nextSibling);
  }
  const url = `${window.location.origin}/${gameId}`;
  invite.innerHTML = `
    <div class="w-full flex flex-col items-center">
      <span class="text-base font-medium mb-1">Andere einladen:</span>
      <div class="flex w-full gap-2 items-center justify-center">
        <input id="invite-url" value="${url}" readonly class="input text-sm w-full max-w-[260px] border-2 border-indigo-200" style="margin:0;">
        <button id="copy-invite" class="btn text-sm px-3 py-1">Kopieren</button>
      </div>
      <span id="copy-invite-feedback" class="text-green-600 text-xs mt-1 hidden">Kopiert!</span>
    </div>
  `;
  document.getElementById("copy-invite").onclick = function() {
    const input = document.getElementById("invite-url");
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand("copy");
    const feedback = document.getElementById("copy-invite-feedback");
    feedback.classList.remove("hidden");
    setTimeout(() => feedback.classList.add("hidden"), 1200);
  };
}

async function updatePlayerSelect() {
  const players = await (await fetch(`/${gameId}/players`)).json();
  const res = await fetch(`/${gameId}/reveal/${playerId}`);
  const revealData = await res.json();
  assignedTargets = new Set(Object.keys(revealData.characters).map(name => {
    for (const [pid, n] of Object.entries(players)) {
      if (n === name) return pid;
    }
    return null;
  }).filter(Boolean));
  const select = document.getElementById("target");
  const current = select.value;
  select.innerHTML = "";
  for (const [id, n] of Object.entries(players)) {
    if (id !== playerId && !assignedTargets.has(id)) {
      let opt = document.createElement("option");
      opt.value = id;
      opt.innerText = n;
      select.appendChild(opt);
    }
  }
  if (current && select.querySelector(`option[value="${current}"]`)) {
    select.value = current;
  }
  document.getElementById("character").disabled = select.options.length === 0;
  document.getElementById("target").disabled = select.options.length === 0;
  document.getElementById("choose").querySelector("button").disabled = select.options.length === 0;
}

async function join(rejoin=false) {
  const nameInput = document.getElementById("name");
  let name = "";
  if (rejoin) {
    name = await fetchOwnName();
    if (name) {
      playerName = name;
      nameInput.value = name;
      nameInput.disabled = true;
      nameInput.classList.add("opacity-60");
      document.querySelector("#setup button").disabled = true;
      document.querySelector("#setup button").classList.add("opacity-60");
    }
  } else {
    name = nameInput.value;
  }
  let payload = { name };
  if (playerId) payload.player_id = playerId;
  console.log(payload);
  const res = await fetch(`/${gameId}/join`, {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  playerId = data.player_id;
  playerName = data.name;
  if (!window.location.search.includes("player_id=" + playerId)) {
    const url = new URL(window.location);
    url.searchParams.set("player_id", playerId);
    window.history.replaceState({}, "", url);
  }
  updateMenu();
  const revealRes = await fetch(`/${gameId}/reveal/${playerId}`);
  const revealData = await revealRes.json();
  if (revealData.assigned) {
    document.getElementById("setup").classList.add("hidden");
    document.getElementById("choose").classList.add("hidden");
    document.getElementById("result").classList.remove("hidden");
    showResult(revealData.characters);
    startResultAutoUpdate();
    stopPlayerSelectAutoUpdate();
  } else {
    document.getElementById("setup").classList.add("hidden");
    document.getElementById("choose").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");
    await updatePlayerSelect();
    startPlayerSelectAutoUpdate();
    stopResultAutoUpdate();
  }
}

async function submitCharacter() {
 const for_player = document.getElementById("target").value;
 const character = document.getElementById("character").value;
 try {
   const resp = await fetch(`/${gameId}/set`, {
     method: "POST",
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ from_player: playerId, for_player, character })
   });
   if (!resp.ok) {
     const data = await resp.json();
     alert(data.error || "Fehler beim Absenden.");
     return;
   }
 } catch (e) {
   alert("Fehler beim Absenden.");
   return;
 }
 document.getElementById("choose").classList.add("hidden");
 document.getElementById("result").classList.remove("hidden");
 stopPlayerSelectAutoUpdate();
 startResultAutoUpdate();

 const revealRes = await fetch(`/${gameId}/reveal/${playerId}`);
 const revealData = await revealRes.json();
 showResult(revealData.characters);
}

function showResult(characters) {
  const ul = document.getElementById("list");
  ul.innerHTML = "";
  const colorPalette = [
    "bg-pink-400", "bg-indigo-400", "bg-emerald-400", "bg-yellow-400",
    "bg-blue-400", "bg-fuchsia-500", "bg-orange-400", "bg-cyan-400"
  ];
  for (const [name, figure] of Object.entries(characters)) {
    let hash = 0;
    for (let i = 0; i < figure.length; i++) hash = figure.charCodeAt(i) + ((hash << 5) - hash);
    const color = colorPalette[Math.abs(hash) % colorPalette.length];
    let li = document.createElement("li");
    li.className = `flex items-center gap-2 mb-2`;
    li.innerHTML = `
      <span class="text-gray-900 font-semibold text-base">${name}</span>
      <span class="text-gray-700 font-medium text-base">ist</span>
      <span class="px-3 py-1 rounded-full text-white font-semibold text-base shadow ${color}">${figure}</span>
    `;
    ul.appendChild(li);
  }
}

function startPlayerSelectAutoUpdate() {
  if (!updatePlayersInterval) {
    updatePlayersInterval = setInterval(updatePlayerSelect, 2000);
  }
}
function stopPlayerSelectAutoUpdate() {
  if (updatePlayersInterval) {
    clearInterval(updatePlayersInterval);
    updatePlayersInterval = null;
  }
}

function startResultAutoUpdate() {
  if (!updateResultInterval) {
    updateResultInterval = setInterval(async () => {
      const revealRes = await fetch(`/${gameId}/reveal/${playerId}`);
      const revealData = await revealRes.json();
      showResult(revealData.characters);
      updateMenu();
    }, 2000);
  }
}
function stopResultAutoUpdate() {
  if (updateResultInterval) {
    clearInterval(updateResultInterval);
    updateResultInterval = null;
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  playerId = getPlayerIdFromUrl();
  if (playerId) {
    await join(true);
  } else {
    document.getElementById("setup").classList.remove("hidden");
  }
});

function updateMenu() {
  let menu = document.getElementById("player-menu");
  if (!menu) {
    menu = document.createElement("div");
    menu.id = "player-menu";
    menu.className = "mb-4 p-3 rounded-xl bg-indigo-50 border border-indigo-200 flex flex-col gap-2 items-start text-left";
    document.querySelector(".bg-white").insertBefore(menu, document.querySelector(".bg-white").firstChild.nextSibling);
  }
  const gameUrl = `${window.location.origin}/${gameId}`;
  const rejoinUrl = `${window.location.origin}/${gameId}?player_id=${playerId}`;
  menu.innerHTML = `
    <div class="flex flex-col gap-1 w-full">
      <div class="flex flex-col items-center w-full mb-2">
        <span class="block text-lg font-bold text-white bg-gradient-to-r from-fuchsia-500 to-indigo-500 px-4 py-2 rounded-full shadow-lg tracking-wide mb-1" style="letter-spacing:0.03em;">
          Du bist: <span class="uppercase tracking-wider">${playerName ? playerName : "-"}</span>
        </span>
      </div>
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-700">Spiel-Link:</span>
        <input id="menu-game-url" value="${gameUrl}" readonly class="input text-xs w-[170px] border-2 border-indigo-200 bg-white" style="margin:0;">
        <button id="menu-copy-game" class="btn text-xs px-2 py-1">Kopieren</button>
        <span id="menu-copy-game-feedback" class="text-green-600 text-xs hidden">Kopiert!</span>
      </div>
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-700">Dein Link:</span>
        <input id="menu-rejoin-url" value="${rejoinUrl}" readonly class="input text-xs w-[170px] border-2 border-indigo-200 bg-white" style="margin:0;">
        <button id="menu-copy-rejoin" class="btn text-xs px-2 py-1">Kopieren</button>
        <span id="menu-copy-rejoin-feedback" class="text-green-600 text-xs hidden">Kopiert!</span>
      </div>
    </div>
  `;
  document.getElementById("menu-copy-game").onclick = function() {
    const input = document.getElementById("menu-game-url");
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand("copy");
    const feedback = document.getElementById("menu-copy-game-feedback");
    feedback.classList.remove("hidden");
    setTimeout(() => feedback.classList.add("hidden"), 1200);
  };
  document.getElementById("menu-copy-rejoin").onclick = function() {
    const input = document.getElementById("menu-rejoin-url");
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand("copy");
    const feedback = document.getElementById("menu-copy-rejoin-feedback");
    feedback.classList.remove("hidden");
    setTimeout(() => feedback.classList.add("hidden"), 1200);
  };
}
