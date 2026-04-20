// DengFOC V0.5 - 双功能电机控制
// 功能1: 实时获取转动信息（角度、速度、方向）
// 功能2: 阻尼控制（粘性阻尼）
//
// 串口协议:
//   M0_angle     -> 查询电机M0当前角度（度）
//   M0_velocity  -> 查询电机M0当前速度（rad/s）
//   M0_damping=X -> 设置M0阻尼系数 X（0.0 ~ 1.0），0=无阻尼，1=最大阻尼
//   M1_angle     -> 查询电机M1当前角度（度）
//   M1_velocity  -> 查询电机M1当前速度（rad/s）
//   M1_damping=X -> 设置M1阻尼系数 X
//   status       -> 显示当前所有状态
//   help         -> 显示帮助信息
//
// 输出格式（轮询时）:
//   M0: angle=123.45 vel=5.67 dir=CW
//   M1: angle=67.89 vel=-3.21 dir=CCW
//
// 灯哥开源，遵循GNU协议

#include "DengFOC.h"

// ============ 配置 ============
int Sensor_DIR = -1;    // 传感器方向（根据实际接线调整：1 或 -1）
int Motor_PP = 7;       // 电机极对数（根据你的电机调整）
float voltage_power_supply = 12.6;  // 供电电压

// ============ 阻尼参数 ============
// 阻尼系数：0.0 = 无阻尼，1.0 = 最大阻尼（仍可转动但很费力）
float M0_damping = 0.0;   // M0 电机阻尼系数
float M1_damping = 0.0;   // M1 电机阻尼系数

// 阻尼力换算系数：damping_voltage = damping_coeff * MAX_DAMPING_VOLT
// MAX_DAMPING_VOLT = voltage_power_supply / 2，即最大能将电压加到供电电压一半
#define MAX_DAMPING_VOLT (voltage_power_supply / 2.0f)

// ============ 上次输出时间（用于限速） ============
unsigned long last_output_time = 0;
#define OUTPUT_INTERVAL_MS 50  // 每50ms输出一次（约20Hz）

// ============ 串口解析 ============
String serialReceiveCommand() {
  static String received_chars;
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (received_chars.length() > 0) {
        String cmd = received_chars;
        received_chars = "";
        return cmd;
      }
    } else {
      received_chars += c;
    }
  }
  return "";
}

// 处理阻尼设置命令
void setDamping(String cmd) {
  int eqPos = cmd.indexOf('=');
  if (eqPos < 0) return;
  String valStr = cmd.substring(eqPos + 1);
  float val = valStr.toFloat();
  val = constrain(val, 0.0f, 1.0f);
  
  if (cmd.startsWith("M0_damping")) {
    M0_damping = val;
    Serial.print("M0 damping set to: ");
    Serial.println(val, 2);
  } else if (cmd.startsWith("M1_damping")) {
    M1_damping = val;
    Serial.print("M1 damping set to: ");
    Serial.println(val, 2);
  }
}

// 打印帮助
void printHelp() {
  Serial.println("========== DengFOC 双功能控制 ==========");
  Serial.println("查询命令:");
  Serial.println("  M0_angle    - 查询电机M0当前角度(度)");
  Serial.println("  M0_velocity - 查询电机M0当前速度(rad/s)");
  Serial.println("  M1_angle    - 查询电机M1当前角度(度)");
  Serial.println("  M1_velocity - 查询电机M1当前速度(rad/s)");
  Serial.println("  status      - 显示所有状态");
  Serial.println("  help        - 显示此帮助");
  Serial.println("");
  Serial.println("阻尼设置:");
  Serial.println("  M0_damping=0.5  - 设置M0阻尼系数(0.0~1.0)");
  Serial.println("  M1_damping=0.5  - 设置M1阻尼系数(0.0~1.0)");
  Serial.println("");
  Serial.println("阻尼效果: 系数越大，转动时阻力越大");
  Serial.println("=========================================");
}

// 打印状态
void printStatus() {
  float a0 = DFOC_M0_Angle() * 180.0f / PI;
  float v0 = DFOC_M0_Velocity();
  float a1 = DFOC_M1_Angle() * 180.0f / PI;
  float v1 = DFOC_M1_Velocity();
  
  Serial.println("========== 当前状态 ==========");
  Serial.print("M0: angle="); Serial.print(a0, 2);
  Serial.print("  vel="); Serial.print(v0, 4);
  Serial.print("  dir="); Serial.println(v0 >= 0 ? "CW" : "CCW");
  Serial.print("M1: angle="); Serial.print(a1, 2);
  Serial.print("  vel="); Serial.print(v1, 4);
  Serial.print("  dir="); Serial.println(v1 >= 0 ? "CW" : "CCW");
  Serial.print("M0 damping: "); Serial.println(M0_damping, 2);
  Serial.print("M1 damping: "); Serial.println(M1_damping, 2);
  Serial.println("================================");
}

// 应用阻尼力
// 原理：粘性阻尼力 = -damping_coeff * velocity（方向与速度相反）
void applyDamping() {
  // M0 电机
  if (M0_damping > 0.0f) {
    float vel = DFOC_M0_Velocity();
    // 阻尼电压：与速度方向相反
    float damping_voltage = -M0_damping * MAX_DAMPING_VOLT * (vel / (abs(vel) + 0.001f));
    // 限幅在 ±voltage_power_supply/2
    damping_voltage = constrain(damping_voltage, -MAX_DAMPING_VOLT, MAX_DAMPING_VOLT);
    M0_setTorque(damping_voltage, S0_electricalAngle());
  }
  
  // M1 电机
  if (M1_damping > 0.0f) {
    float vel = DFOC_M1_Velocity();
    float damping_voltage = -M1_damping * MAX_DAMPING_VOLT * (vel / (abs(vel) + 0.001f));
    damping_voltage = constrain(damping_voltage, -MAX_DAMPING_VOLT, MAX_DAMPING_VOLT);
    M1_setTorque(damping_voltage, S1_electricalAngle());
  }
}

// 定期输出电机状态（限速）
void periodicOutput() {
  unsigned long now = millis();
  if (now - last_output_time >= OUTPUT_INTERVAL_MS) {
    float a0 = DFOC_M0_Angle() * 180.0f / PI;
    float v0 = DFOC_M0_Velocity();
    float a1 = DFOC_M1_Angle() * 180.0f / PI;
    float v1 = DFOC_M1_Velocity();
    
    Serial.print("M0: angle="); Serial.print(a0, 2);
    Serial.print(" vel="); Serial.print(v0, 4);
    Serial.print(" dir="); Serial.println(v0 >= 0 ? "CW" : "CCW");
    
    Serial.print("M1: angle="); Serial.print(a1, 2);
    Serial.print(" vel="); Serial.print(v1, 4);
    Serial.print(" dir="); Serial.println(v1 >= 0 ? "CW" : "CCW");
    
    last_output_time = now;
  }
}

// ============ 初始化 ============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("DengFOC 双功能控制初始化...");
  
  // 设置供电电压
  DFOC_Vbus(voltage_power_supply);
  
  // 初始化编码器并校准
  DFOC_M0_alignSensor(Motor_PP, Sensor_DIR);
  DFOC_M1_alignSensor(Motor_PP, Sensor_DIR);
  
  // 使能电机
  DFOC_enable();
  
  // 打印帮助
  printHelp();
  Serial.println("初始化完成，请输入命令或设置阻尼");
}

// ============ 主循环 ============
void loop() {
  // 1. 处理串口命令
  String cmd = serialReceiveCommand();
  if (cmd.length() > 0) {
    cmd.trim();
    
    if (cmd == "help") {
      printHelp();
    }
    else if (cmd == "status") {
      printStatus();
    }
    else if (cmd == "M0_angle") {
      float a = DFOC_M0_Angle() * 180.0f / PI;
      Serial.print("M0 angle: ");
      Serial.print(a, 4);
      Serial.println(" deg");
    }
    else if (cmd == "M0_velocity") {
      float v = DFOC_M0_Velocity();
      Serial.print("M0 velocity: ");
      Serial.print(v, 4);
      Serial.println(" rad/s");
    }
    else if (cmd == "M1_angle") {
      float a = DFOC_M1_Angle() * 180.0f / PI;
      Serial.print("M1 angle: ");
      Serial.print(a, 4);
      Serial.println(" deg");
    }
    else if (cmd == "M1_velocity") {
      float v = DFOC_M1_Velocity();
      Serial.print("M1 velocity: ");
      Serial.print(v, 4);
      Serial.println(" rad/s");
    }
    else if (cmd.startsWith("M0_damping=") || cmd.startsWith("M1_damping=")) {
      setDamping(cmd);
    }
    else {
      Serial.print("Unknown command: ");
      Serial.println(cmd);
      Serial.println("Type 'help' for available commands");
    }
  }
  
  // 2. 应用阻尼力
  applyDamping();
  
  // 3. 定期输出状态（每50ms）
  periodicOutput();
}
