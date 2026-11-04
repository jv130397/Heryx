import { ContactShadows, Environment, Float, Sparkles, useTexture } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";

type Point = [number, number, number];
type AvatarPose = "neutral" | "pointing" | "laptop" | "thinking" | "celebrating";

function Tube({ from, to, color = "#4ad8ff", radius = .018 }: { from: Point; to: Point; color?: string; radius?: number }) {
  const values = useMemo(() => {
    const start = new THREE.Vector3(...from); const end = new THREE.Vector3(...to); const direction = end.clone().sub(start);
    return { midpoint: start.clone().add(end).multiplyScalar(.5), length: direction.length(), quaternion: new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize()) };
  }, [from, to]);
  return <mesh position={values.midpoint} quaternion={values.quaternion}><cylinderGeometry args={[radius, radius, values.length, 10]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={3} toneMapped={false} /></mesh>;
}

function Hologram({ introPhase }: { introPhase: number }) {
  const group = useRef<THREE.Group>(null);
  useFrame((state, delta) => { if (group.current) { group.current.rotation.y = Math.sin(state.clock.elapsedTime * .22) * .08; const target = introPhase >= 2 ? 1 : .001; const scale = THREE.MathUtils.damp(group.current.scale.x, target, 3.5, delta); group.current.scale.setScalar(scale); } });
  const nodes: Array<[number, number, number, "square" | "circle"]> = [[-1.2,.8,0,"square"],[0,.8,0,"circle"],[1.25,.8,0,"square"],[-.65,-.2,0,"circle"],[.65,-.2,0,"square"],[0,-1.15,0,"circle"]];
  const links: Array<[Point,Point]> = [[[-1.2,.8,0],[0,.8,0]],[[.6,.8,0],[1.25,.8,0]],[[-.6,.8,0],[-.6,-.2,0]],[[.6,.8,0],[.6,-.2,0]],[[-.65,-.2,0],[.65,-.2,0]],[[0,-.2,0],[0,-1.15,0]]];
  return <Float speed={.7} floatIntensity={.12} rotationIntensity={.02}><group ref={group} position={[2.45,2.25,-1.35]} rotation={[-.08,-.2,0]}>
    {links.map(([from,to], index) => <Tube key={index} from={from} to={to} />)}
    {nodes.map(([x,y,z,shape], index) => <mesh key={index} position={[x,y,z]} rotation={shape === "circle" ? [Math.PI/2,0,0] : [0,0,0]}>{shape === "circle" ? <cylinderGeometry args={[.18,.18,.06,32]} /> : <boxGeometry args={[.34,.34,.07]} />}<meshPhysicalMaterial color="#aaf3ff" emissive="#2fd4ff" emissiveIntensity={2.8} transparent opacity={.78} transmission={.35} /></mesh>)}
    <pointLight color="#49dfff" intensity={5} distance={5} />
  </group></Float>;
}

function Avatar({ introPhase, pose }: { introPhase: number; pose: AvatarPose }) {
  const source = useTexture("/assets/joao-vitor-game-avatar.png");
  const texture = useMemo(() => source.clone(), [source]);
  const avatar = useRef<THREE.Group>(null);
  useEffect(() => { const activePose = introPhase === 1 || introPhase === 2 ? "pointing" : pose; const frames: Record<AvatarPose,[number,number]> = { neutral:[0,.5], pointing:[1/3,.5], laptop:[2/3,.5], thinking:[0,0], celebrating:[1/3,0] }; texture.needsUpdate = true; texture.repeat.set(1 / 3,1 / 2); texture.offset.set(...frames[activePose]); texture.colorSpace = THREE.SRGBColorSpace; texture.magFilter = THREE.NearestFilter; }, [texture,introPhase,pose]);
  useFrame((state,delta) => { if (avatar.current) { avatar.current.position.y = Math.sin(state.clock.elapsedTime * 1.25) * .035; const target = pose === "neutral" ? 1 : 1.035; const scale = THREE.MathUtils.damp(avatar.current.scale.x,target,6,delta); avatar.current.scale.setScalar(scale); } });
  return <group ref={avatar} position={[-.35,.2,.7]} rotation={[0,.12,0]}>
    <mesh castShadow><planeGeometry args={[2.65,2.65]} /><meshBasicMaterial map={texture} transparent toneMapped={false} /></mesh>
    <pointLight position={[0,1,.8]} color="#17d5ec" intensity={1.5} distance={4} />
  </group>;
}

function Observatory({ introPhase, avatarPose }: { introPhase: number; avatarPose: AvatarPose }) {
  return <group>
    <mesh position={[0,1,-4.8]} rotation={[0,0,0]} receiveShadow><cylinderGeometry args={[7.8,7.8,6.4,48,1,true,Math.PI*.08,Math.PI*.84]} /><meshStandardMaterial color="#07141d" side={THREE.BackSide} metalness={.72} roughness={.3} /></mesh>
    <mesh position={[0,-1.2,0]} receiveShadow><cylinderGeometry args={[6.4,6.8,.45,64]} /><meshStandardMaterial color="#0c1b25" metalness={.88} roughness={.24} /></mesh>
    <mesh position={[0,-.96,0]} rotation={[-Math.PI/2,0,0]} receiveShadow><circleGeometry args={[6.35,64]} /><meshStandardMaterial color="#07131b" metalness={.9} roughness={.22} /></mesh>
    {[2.25,3.8,5.35].map((radius) => <mesh key={radius} position={[0,-.94,0]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[radius,radius+.055,96]} /><meshBasicMaterial color="#20d7ef" transparent opacity={radius === 3.8 ? .72 : .36} toneMapped={false} /></mesh>)}
    {[-5.4,-3.6,-1.8,0,1.8,3.6,5.4].map((x) => <group key={x} position={[x,.3,-4.3 + Math.abs(x)*.09]}><mesh><boxGeometry args={[.1,2.8,.08]} /><meshStandardMaterial color="#16485a" emissive="#13cce9" emissiveIntensity={2.2} /></mesh><pointLight position={[0,0,.5]} color="#20d9f2" intensity={.45} distance={2.2} /></group>)}
    <mesh position={[2.45,1.25,-1.5]} rotation={[0,0,Math.PI]}><coneGeometry args={[1.6,3.2,48,1,true]} /><meshBasicMaterial color="#2edaf2" transparent opacity={.035} side={THREE.DoubleSide} depthWrite={false} /></mesh>
    <mesh position={[2.45,.05,-1.35]} castShadow><cylinderGeometry args={[1.35,1.6,.36,32]} /><meshStandardMaterial color="#122837" metalness={.75} roughness={.25} /></mesh>
    <mesh position={[2.45,.19,-1.35]}><cylinderGeometry args={[1.38,1.38,.12,48]} /><meshStandardMaterial color="#07131a" metalness={.82} roughness={.18} /></mesh>
    <mesh position={[2.45,.27,-1.35]}><cylinderGeometry args={[1.08,1.25,.055,48]} /><meshStandardMaterial color="#b9f8ff" emissive="#20d7ef" emissiveIntensity={2.5} /></mesh>
    <mesh position={[2.45,.12,-1.35]} rotation={[Math.PI/2,0,0]}><torusGeometry args={[1.39,.035,12,64]} /><meshBasicMaterial color="#20d9f1" toneMapped={false} /></mesh>
    <mesh position={[2.45,-.04,-1.35]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[1.38,1.49,64]} /><meshBasicMaterial color="#23d9f1" toneMapped={false} /></mesh>
    <Hologram introPhase={introPhase} /><Avatar introPhase={introPhase} pose={avatarPose} /><Sparkles count={55} scale={[12,6,8]} size={1.2} speed={.15} color="#68ddf5" opacity={.45} />
    <ContactShadows position={[0,-.91,0]} opacity={.68} scale={12} blur={2.6} far={4.5} color="#001018" />
  </group>;
}

function CameraRig({ reducedMotion, entered }: { reducedMotion: boolean; entered: boolean }) {
  const { camera, pointer } = useThree();
  useFrame((_, delta) => {
    const targetX = reducedMotion ? 0 : pointer.x * .45; const targetY = reducedMotion ? 1.05 : 1.05 + pointer.y * .22;
    camera.position.x = THREE.MathUtils.damp(camera.position.x,targetX,2.5,delta); camera.position.y = THREE.MathUtils.damp(camera.position.y,targetY,2.5,delta); camera.position.z = THREE.MathUtils.damp(camera.position.z,entered ? 7.4 : 9.4,1.4,delta); camera.lookAt(0,.55,-.5);
  });
  return null;
}

export function PedigreeScene({ reducedMotion, entered, introPhase, avatarPose }: { reducedMotion: boolean; entered: boolean; introPhase: number; avatarPose: AvatarPose }) {
  return <div className="scene" aria-label="Observatório genômico tridimensional interativo"><Canvas shadows dpr={[1,1.75]} camera={{ position:[0,1.05,9.4],fov:43,near:.1,far:100 }} gl={{ antialias:true,alpha:true,powerPreference:"high-performance",toneMapping:THREE.ACESFilmicToneMapping,toneMappingExposure:1.12 }}>
    <color attach="background" args={["#03090f"]} /><fog attach="fog" args={["#03090f",8,21]} /><ambientLight intensity={.42} />
    <directionalLight position={[-3,7,5]} intensity={3.4} color="#d6f6ff" castShadow shadow-mapSize={[1024,1024]} /><spotLight position={[2,7,1]} intensity={8} color="#2bdcff" angle={.42} penumbra={1} castShadow /><pointLight position={[-4,1,2]} intensity={5} color="#4656ff" distance={9} />
    <Observatory introPhase={introPhase} avatarPose={avatarPose} /><CameraRig reducedMotion={reducedMotion} entered={entered} /><Environment preset="night" environmentIntensity={.22} />
  </Canvas></div>;
}
