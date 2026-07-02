const poseImages: Record<string, string> = {
  tree: "/assets/yoga-poses/vrikshasana.png",
  warrior_i: "/assets/yoga-poses/virbhadrasana-i.png",
  warrior_ii: "/assets/yoga-poses/virbhadrasana-ii.png",
  warrior_iii: "/assets/yoga-poses/virbhadrasana-iii.png",
  cobra: "/assets/yoga-poses/bhujangasana.png",
  bow: "/assets/yoga-poses/dhanurasana.png",
  archer: "/assets/yoga-poses/akarna-dhanurasana.png",
  camel: "/assets/yoga-poses/ushtrasana.png",
  shoulder_stand: "/assets/yoga-poses/sarvangasana.png",
  mountain: "/assets/yoga-poses/tadasana.png",
  wind_relieving: "/assets/yoga-poses/pavanmukhasana.png",
  thunderbolt: "/assets/yoga-poses/vajrasana.png",
};

export interface PoseInfo {
  /** Stable id sent to the backend to select the rule engine. */
  id: string;
  name: string;
  sanskrit: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  focus: string;
  description: string;
  cues: string[];
  image: string;
}

export const POSES: PoseInfo[] = [
  {
    id: "tree",
    name: "Tree Pose",
    sanskrit: "Vrikshasana",
    difficulty: "Beginner",
    focus: "Balancing / Standing",
    description:
      "A balancing standing pose that targets the calves, quadriceps, ankles, and core. Improves balance, coordination, and lower-body stabilization.",
    cues: ["Straighten your standing leg", "Lift the raised foot higher", "Bring hands to chest or above head"],
    image: poseImages.tree,
  },
  {
    id: "warrior_i",
    name: "Warrior I",
    sanskrit: "Virabhadrasana I",
    difficulty: "Beginner",
    focus: "Standing / Backbend",
    description:
      "A strong standing lunge that engages quadriceps, hip flexors, shoulders, and calves. Builds lower-body strength, opens the chest, and deepens hip-flexor flexibility.",
    cues: ["Bend your front knee deeper", "Straighten your back leg", "Raise your arms higher overhead"],
    image: poseImages.warrior_i,
  },
  {
    id: "warrior_ii",
    name: "Warrior II",
    sanskrit: "Virabhadrasana II",
    difficulty: "Beginner",
    focus: "Standing / Lateral Open",
    description:
      "A grounded standing pose that works the quadriceps, inner thighs, and shoulders. Enhances stamina, opens the hips, and tones the core and deltoids.",
    cues: ["Bend your front knee deeper", "Keep both arms parallel to the floor", "Keep torso upright"],
    image: poseImages.warrior_ii,
  },
  {
    id: "warrior_iii",
    name: "Warrior III",
    sanskrit: "Virabhadrasana III",
    difficulty: "Intermediate",
    focus: "Balancing / Forward Bend",
    description:
      "A powerful balance pose for the hamstrings, glutes, core, and spinal extensors. Develops core strength, full-body coordination, and single-leg stability.",
    cues: ["Straighten your standing leg", "Lift the back leg to hip level", "Reach arms forward"],
    image: poseImages.warrior_iii,
  },
  {
    id: "cobra",
    name: "Cobra Pose",
    sanskrit: "Bhujangasana",
    difficulty: "Beginner",
    focus: "Prone / Backbend",
    description:
      "A gentle backbend that strengthens the spine, glutes, chest, and triceps while stimulating the abdominal organs.",
    cues: ["Lift your chest higher", "Keep your hips grounded", "Keep a micro-bend in the elbows"],
    image: poseImages.cobra,
  },
  {
    id: "bow",
    name: "Bow Pose",
    sanskrit: "Dhanurasana",
    difficulty: "Intermediate",
    focus: "Prone / Backbend",
    description:
      "A deep backbend that works the abs, back extensors, chest, and quads. Massages abdominal organs, corrects slouching posture, and expands lung capacity.",
    cues: ["Lift your chest and thighs", "Kick feet into your hands", "Draw shoulders back"],
    image: poseImages.bow,
  },
  {
    id: "archer",
    name: "Archer Pose",
    sanskrit: "Akarna Dhanurasana",
    difficulty: "Advanced",
    focus: "Seated / Core Twist",
    description:
      "A seated twist that targets the hamstrings, groin, core, and shoulders. Increases hip mobility, builds abdominal compression strength, and sharpens focus.",
    cues: ["Draw the foot toward your ear", "Keep the extended leg straight", "Sit tall through the spine"],
    image: poseImages.archer,
  },
  {
    id: "camel",
    name: "Camel Pose",
    sanskrit: "Ustrasana",
    difficulty: "Intermediate",
    focus: "Kneeling / Backbend",
    description:
      "A deep kneeling backbend that opens the hip flexors, quadriceps, abs, and throat. Opens the front body, stretches deep hip flexors, and improves spinal flexibility.",
    cues: ["Open your chest toward the ceiling", "Reach hands to your heels", "Keep hips over the knees"],
    image: poseImages.camel,
  },
  {
    id: "shoulder_stand",
    name: "Shoulder Stand",
    sanskrit: "Sarvangasana",
    difficulty: "Advanced",
    focus: "Inversion",
    description:
      "An inversion that strengthens the neck, upper back, core, and shoulders while calming the nervous system and improving circulation.",
    cues: ["Extend legs straight up", "Stack hips over shoulders", "Support your back with your hands"],
    image: poseImages.shoulder_stand,
  },
  {
    id: "mountain",
    name: "Mountain Pose",
    sanskrit: "Tadasana",
    difficulty: "Beginner",
    focus: "Standing / Alignment",
    description:
      "The foundational standing alignment pose for core, legs, ankles, and posture muscles. Fixes spinal alignment and enhances grounding.",
    cues: ["Stand tall through the crown", "Level your shoulders", "Ground evenly through both feet"],
    image: poseImages.mountain,
  },
  {
    id: "wind_relieving",
    name: "Wind-Relieving Pose",
    sanskrit: "Pawanmuktasana",
    difficulty: "Beginner",
    focus: "Supine / Compression",
    description:
      "A supine compression pose that eases the low back, glutes, and abdominals. Relieves digestive gas, eases lower back tension, and gently stretches the spine.",
    cues: ["Hug knees toward the chest", "Keep shoulders relaxed", "Lengthen the lower back"],
    image: poseImages.wind_relieving,
  },
  {
    id: "thunderbolt",
    name: "Thunderbolt Pose",
    sanskrit: "Vajrasana",
    difficulty: "Beginner",
    focus: "Seated / Kneeling",
    description:
      "A seated kneeling pose that supports the quadriceps, ankles, and pelvic muscles. Safe after meals, aids digestion, and tones the pelvic floor.",
    cues: ["Sit tall through the spine", "Rest hands on the thighs", "Relax the shoulders"],
    image: poseImages.thunderbolt,
  },
];

export function getPose(id: string): PoseInfo | undefined {
  return POSES.find((p) => p.id === id);
}