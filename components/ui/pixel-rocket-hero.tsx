"use client";

import React, { useRef, useEffect } from "react";
import { motion, useAnimation } from "framer-motion";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { HudButton } from "./hud-button";

interface PixelRocketHeroProps {
  onLaunch?: () => void;
}

// --- Main Hero Component ---
export const PixelRocketHero: React.FC<PixelRocketHeroProps> = ({ onLaunch }) => {
  const textControls = useAnimation();
  const buttonControls = useAnimation();

  useEffect(() => {
    // Add pixel font to the document head
    const link = document.createElement("link");
    link.href = "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap";
    link.rel = "stylesheet";
    document.head.appendChild(link);

    textControls.start((i) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.05 + 1.2,
        duration: 1.0,
        ease: [0.2, 0.65, 0.3, 0.9],
      },
    }));
    buttonControls.start({
      opacity: 1,
      y: 0,
      transition: { delay: 2.2, duration: 0.8 },
    });

    return () => {
      if (document.head.contains(link)) {
        document.head.removeChild(link);
      }
    };
  }, [textControls, buttonControls]);

  const headline = "To the Moon!";

  return (
    <div
      className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden bg-[#070b19] text-white selection:bg-pink-500 selection:text-white"
      style={{ fontFamily: "'Press Start 2P', monospace, system-ui" }}
    >
      <PixelVoyagerCanvas />
      <HeroNav />

      <div className="relative z-10 mx-auto max-w-4xl text-center px-4">
        {/* Top Status Telemetry */}
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/40 px-4 py-1.5 text-xs text-cyan-300 backdrop-blur-md">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>SECTOR 07 // WARP VELOCITY ONLINE</span>
        </div>

        {/* 3D Pixel Headline */}
        <h1
          className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl md:text-7xl select-none"
          style={{
            textShadow:
              "4px 4px 0px #ff007f, 7px 7px 0px #7928ca, 0 0 25px rgba(255, 0, 127, 0.4)",
          }}
        >
          {headline.split("").map((char, i) => (
            <motion.span
              key={i}
              custom={i}
              initial={{ opacity: 0, y: 40 }}
              animate={textControls}
              style={{ display: "inline-block" }}
            >
              {char === " " ? "\u00A0" : char}
            </motion.span>
          ))}
        </h1>

        {/* Subtitle */}
        <motion.p
          custom={headline.length}
          initial={{ opacity: 0, y: 20 }}
          animate={textControls}
          className="mx-auto mt-6 max-w-2xl text-xs sm:text-sm md:text-base leading-relaxed text-slate-300 font-sans tracking-wide"
        >
          Embark on a new cosmic journey. Explore decentralized galaxies, defeat your deadlines,
          and claim your stake in the pixelated productivity universe.
        </motion.p>

        {/* Sci-Fi HUD Launch Mission Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={buttonControls}
          className="mt-8 flex justify-center"
        >
          <HudButton
            variant="primary"
            style="style1"
            size="large"
            onClick={onLaunch}
          >
            <span className="flex items-center gap-2 tracking-wider">
              <span>🚀</span>
              <span>LAUNCH MISSION</span>
            </span>
          </HudButton>
        </motion.div>
      </div>
    </div>
  );
};

// --- Navigation Component ---
const HeroNav: React.FC = () => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0, transition: { delay: 0.6, duration: 0.8 } }}
      className="absolute top-0 left-0 right-0 z-20 p-6 backdrop-blur-sm bg-black/20 border-b border-cyan-500/20"
    >
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="text-2xl animate-bounce">🚀</span>
          <span className="text-lg font-bold tracking-widest text-cyan-400 drop-shadow-[0_0_10px_#00f0ff]">
            VOYAGER
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs font-sans">
          <span className="text-slate-400">STATUS:</span>
          <span className="text-emerald-400 font-mono">MISSION_READY</span>
        </div>
      </div>
    </motion.nav>
  );
};

// --- Three.js Canvas Component ---
const PixelVoyagerCanvas: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    const currentMount = mountRef.current;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x060919, 0.015);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 25;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    const mouse = new THREE.Vector2(0, 0);
    const clock = new THREE.Clock();

    // Post-processing for bloom effect
    const renderScene = new RenderPass(scene, camera);
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.5,
      0.4,
      0.85
    );
    bloomPass.threshold = 0.05;
    bloomPass.strength = 1.35;
    bloomPass.radius = 0.4;

    const composer = new EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);

    // --- Starfield ---
    const starGeometry = new THREE.BufferGeometry();
    const starVertices = [];
    const starColors = [];
    for (let i = 0; i < 1800; i++) {
      const x = (Math.random() - 0.5) * 110;
      const y = (Math.random() - 0.5) * 110;
      const z = (Math.random() - 0.5) * 110;
      starVertices.push(x, y, z);

      const color = new THREE.Color();
      if (Math.random() > 0.7) {
        color.setHSL(0.85, 0.9, 0.7); // Pink/purple
      } else if (Math.random() > 0.4) {
        color.setHSL(0.52, 0.9, 0.7); // Cyan
      } else {
        color.setHSL(0.6, 0.1, 0.9); // White/silver
      }
      starColors.push(color.r, color.g, color.b);
    }
    starGeometry.setAttribute("position", new THREE.Float32BufferAttribute(starVertices, 3));
    starGeometry.setAttribute("color", new THREE.Float32BufferAttribute(starColors, 3));
    const starMaterial = new THREE.PointsMaterial({
      size: 0.16,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
    });
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // --- Pixel Rocket ---
    const rocket = new THREE.Group();
    const pixelSize = 0.22;
    const pixelGeo = new THREE.BoxGeometry(pixelSize, pixelSize, pixelSize);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x00d4ff,
      roughness: 0.3,
      metalness: 0.2,
      flatShading: true,
    });
    const wingMat = new THREE.MeshStandardMaterial({
      color: 0xff007f,
      roughness: 0.4,
      flatShading: true,
    });
    const cockpitMat = new THREE.MeshStandardMaterial({
      color: 0x87ceeb,
      emissive: 0x00f0ff,
      emissiveIntensity: 0.8,
      flatShading: true,
    });

    // Body
    for (let y = -4; y < 5; y++) {
      for (let x = -2; x < 3; x++) {
        if (Math.abs(x) === 2 && y > 1) continue;
        const pixel = new THREE.Mesh(pixelGeo, bodyMat);
        pixel.position.set(x * pixelSize, y * pixelSize, 0);
        rocket.add(pixel);
      }
    }
    // Wings
    for (let y = -3; y < -1; y++) {
      for (let x = -4; x < -2; x++) {
        const pixelL = new THREE.Mesh(pixelGeo, wingMat);
        pixelL.position.set(x * pixelSize, y * pixelSize, 0);
        rocket.add(pixelL);
        const pixelR = new THREE.Mesh(pixelGeo, wingMat);
        pixelR.position.set(-x * pixelSize, y * pixelSize, 0);
        rocket.add(pixelR);
      }
    }
    // Cockpit
    const cockpit = new THREE.Mesh(pixelGeo, cockpitMat);
    cockpit.position.set(0, 3 * pixelSize, pixelSize * 0.8);
    rocket.add(cockpit);
    scene.add(rocket);

    // --- Rocket Trail (Object Pooling) ---
    const trailPool: THREE.Mesh[] = [];
    let trailIndex = 0;
    const trailSize = 180;
    const trailGeo = new THREE.BoxGeometry(pixelSize * 1.3, pixelSize * 1.3, pixelSize * 1.3);
    for (let i = 0; i < trailSize; i++) {
      const trailMat = new THREE.MeshBasicMaterial({
        color: Math.random() > 0.5 ? 0xff007f : 0x00f0ff,
        transparent: true,
        opacity: 0.85,
      });
      const particle = new THREE.Mesh(trailGeo, trailMat);
      particle.visible = false;
      scene.add(particle);
      trailPool.push(particle);
    }

    // --- Ambient Floating Crypto / Pixel Coins ---
    const coinGroup = new THREE.Group();
    const coinMat = new THREE.MeshStandardMaterial({
      color: 0xffd700,
      emissive: 0xffaa00,
      emissiveIntensity: 0.35,
      metalness: 0.8,
      roughness: 0.2,
      flatShading: true,
    });
    for (let i = 0; i < 22; i++) {
      const coin = new THREE.Group();
      for (let p = 0; p < 12; p++) {
        const pixel = new THREE.Mesh(pixelGeo, coinMat);
        const angle = (p / 12) * Math.PI * 2;
        pixel.position.set(Math.cos(angle) * 0.45, Math.sin(angle) * 0.45, 0);
        coin.add(pixel);
      }
      coin.position.set(
        (Math.random() - 0.5) * 44,
        (Math.random() - 0.5) * 32,
        (Math.random() - 0.5) * 22
      );
      coinGroup.add(coin);
    }
    scene.add(coinGroup);

    // Directional & Ambient Lighting
    const ambLight = new THREE.AmbientLight(0x223355, 1.5);
    scene.add(ambLight);
    const dirLight = new THREE.DirectionalLight(0x00f0ff, 2.5);
    dirLight.position.set(5, 10, 15);
    scene.add(dirLight);

    const handleMouseMove = (event: MouseEvent) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener("mousemove", handleMouseMove);

    let animationFrameId: number;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Smooth mouse follow
      const targetPosition = new THREE.Vector3(mouse.x * 14, mouse.y * 9, 0);
      rocket.position.lerp(targetPosition, 0.05);
      rocket.rotation.y = (targetPosition.x - rocket.position.x) * 0.12;
      rocket.rotation.x = -(targetPosition.y - rocket.position.y) * 0.12;
      rocket.rotation.z = Math.sin(elapsedTime * 2.5) * 0.05;

      // Emit trail
      if (Math.random() > 0.25) {
        const particle = trailPool[trailIndex];
        particle.position.copy(rocket.position);
        particle.position.y -= 0.85;
        particle.position.x += (Math.random() - 0.5) * 0.2;
        particle.scale.setScalar(1);
        particle.visible = true;
        (particle as any).life = 1.0;
        trailIndex = (trailIndex + 1) % trailSize;
      }

      // Animate trail particles
      trailPool.forEach((p) => {
        const particle = p as any;
        if (particle.visible) {
          particle.life -= delta * 1.6;
          particle.position.y -= delta * 3.5;
          particle.scale.setScalar(Math.max(0, particle.life));
          if (particle.life <= 0) particle.visible = false;
        }
      });

      // Animate coins
      coinGroup.children.forEach((coin, i) => {
        coin.rotation.y = elapsedTime * (i % 2 === 0 ? 1.5 : -1.5);
        coin.position.y += Math.sin(elapsedTime * 1.8 + i) * 0.008;
      });

      // Drift stars
      stars.rotation.y = elapsedTime * 0.02;
      stars.rotation.x = elapsedTime * 0.01;

      composer.render();
    };
    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      composer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return <div ref={mountRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

export default PixelRocketHero;
