PIRATE_PHRASES = {
    "greeting": [
        "Ahoy there, Captain! Ready to inspect the fleet?",
        "Avast ye! Let's see if these YAMLs be seaworthy!",
        "Shiver me timbers! Another day, another inspection!",
        "Hoist the colors! The KubeInspector be aboard!",
        "Yo ho ho! Let's hunt for some missing configs!",
        "Yarr! Time to scrub the deck of these manifests!",
        "Ahoy! Hand over yer YAMLs before I make ye walk the plank!",
        "Batten down the hatches! We're diving into the configs!",
        "Prepare to be boarded! KubeInspector is here!",
        "Weigh anchor and hoist the mizzen! Let's inspect!"
    ],
    "found_issue": [
        "Blimey! We found a leak in the hull!",
        "By Blackbeard's ghost! A misconfiguration!",
        "Avast! What be this mess?",
        "Shiver me timbers! This YAML is taking on water!",
        "Yarr! The code monkeys missed a spot!",
        "Son of a biscuit eater! Look at this missing field!",
        "Dead men tell no tales, and missing configs cause downtime!",
        "Thar she blows! A critical vulnerability!",
        "Sink me! This resource ain't ready for the high seas!",
        "Heave ho! We've got work to do on this one!"
    ],
    "categories": {
        "MANDATORY": "Walk the Plank Critical",
        "RECOMMENDED": "Better Safe Than Sunk",
        "OPTIONAL": "Polishing the Cannons",
        "BONUS": "Treasure Map Extras"
    },
    "applying_fix": [
        "Aye, Captain! Patching the hull now!",
        "Swabbing the deck and applying the fix!",
        "Heaving to and making repairs!",
        "Loading the cannons with YAML fixes!",
        "Yarr! Putting some elbow grease into it!"
    ],
    "fix_complete": [
        "Good as new, Captain! The ship is watertight!",
        "Repairs complete! She'll sail true now!",
        "Fixed it! No more leaks in this manifest!",
        "Yarr! The patch holds strong!",
        "Done and dusted! Let's find more treasure!"
    ],
    "cannot_fix": [
        "Blast it! I can't fix this one without more supplies!",
        "Yarr! Ye'll need to do this manually, Captain!",
        "Avast! This fix be beyond my skills!",
        "Shiver me timbers! I can't patch this leak!",
        "Curses! The damage is too severe for an auto-fix!"
    ],
    "critical_finding": [
        "🚨 [red]{severity}[/red]: {container} in {namespace} be failing '{check_name}'! {details}",
        "💀 [red]{severity}[/red]: Blimey! {container} lacks {check_name}! {details}",
        "💣 [red]{severity}[/red]: {container} will sink us! Failed '{check_name}'! {details}"
    ],
    "recommended_finding": [
        "⚠️ [yellow]{severity}[/yellow]: {container} in {namespace} could use '{check_name}'. {details}",
        "⚓ [yellow]{severity}[/yellow]: Avast, {container} be missin' '{check_name}'. {details}",
        "🔭 [yellow]{severity}[/yellow]: A spyglass shows {container} lacks '{check_name}'. {details}"
    ],
    "optional_finding": [
        "💡 [cyan]{severity}[/cyan]: {container} could be shinier with '{check_name}'. {details}",
        "✨ [cyan]{severity}[/cyan]: Yer {container} might want '{check_name}'. {details}"
    ],
    "report_header": [
        "🏴☠️ THE CAPTAIN'S LOG 🏴☠️",
        "📜 INSPECTION SCROLL 📜",
        "⚓ FLEET STATUS REPORT ⚓"
    ],
    "passed_check": [
        "Passed with flying colors!",
        "Shipshape and Bristol fashion!",
        "Steady as she goes!"
    ],
    "failed_check": [
        "Taking on water!",
        "Prepare the lifeboats!",
        "Mutiny imminent!"
    ],
    "all_clear": [
        "CAPTAIN! The ship be seaworthy! Every sail stitched, every cannon loaded!",
        "Not a leak in sight! This vessel be ready for any storm!",
        "By Neptune's trident, all checks passed! She's a fine ship!"
    ],
    "ready_to_board": [
        "⚓ Captain! YE ARE READY TO BOARD! The sea awaits! 🚢🌊",
        "🏴☠️ All hands accounted for! Board with confidence, Captain! The horizon be yours! ⚓",
        "🌟 The checklist be complete! Captain, yer ship awaits! Set sail! 🚢"
    ],
    "needs_repairs": [
        "The ship's taking on water, Captain! We need repairs!",
        "We can't sail like this! Look at all these leaks!",
        "Batten down the hatches! We've got major issues to fix!"
    ],
    "ship_sinking": [
        "ABANDON SHIP! Too many critical failures!",
        "We're going down to Davy Jones' locker!",
        "The kraken takes us all! Too many missing configs!"
    ],
    "explanations": {
        "RESOURCE-REQ": "Requests are like ballast - they keep yer ship stable by reserving resources. Without 'em, one greedy container can starve the rest.",
        "RESOURCE-LIM": "Limits be the rum ration - prevents one container from consuming the entire ship's supplies.",
        "HPA-MINMAX": "Min/max replicas keep yer crew size in check. Too few and ye sink, too many and ye run out of supplies.",
        "HPA-CPU-MEM": "CPU/Memory metrics guide yer scaling like a compass guides a ship through fog.",
        "HPA-BEHAVIOUR": "Behavior policies prevent yer ship from panicking. Scale up fast, scale down slow - like reefing sails in a squall.",
        "HPA-CUSTOM-RPS": "RPS metric be like counting waves hittin' the hull. More waves = more sailors needed.",
        "HPA-CUSTOM-LATENCY": "Latency metric tells ye if yer ship's responding slowly. Better to know before the crew mutinies!"
    },
    "fix_suggestions": {
        "RESOURCE-REQ": "Add resources.requests.cpu and resources.requests.memory to {container}",
        "RESOURCE-LIM": "Add resources.limits.cpu and resources.limits.memory to {container}",
        "HPA-MINMAX": "Add minReplicas and maxReplicas to HPA for {resource}",
        "HPA-CPU-MEM": "Add CPU or Memory utilization target to HPA metrics",
        "HPA-BEHAVIOUR": "Add scaleUp and scaleDown behavior policies to HPA",
        "HPA-CUSTOM-RPS": "Add Prometheus custom metric for requests_per_second",
        "HPA-CUSTOM-LATENCY": "Add Prometheus custom metric for request_latency_p95"
    },
    "banners": {
        "kubeinspector": "pirate_ship",
        "passed": "checkmark",
        "failed": "crossbones"
    }
}
