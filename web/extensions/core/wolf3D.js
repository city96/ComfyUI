import { app } from "/scripts/app.js";

const ext = {
	name: "3D.Wolf3D",
	async init(app) {
		let script = document.createElement("script");
		script.src = "extensions/core/raycaster.js";
		document.head.appendChild(script);
	}
};
app.registerExtension(ext);
