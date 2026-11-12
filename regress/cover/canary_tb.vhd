library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity canary_tb is
  generic (GEN_ON : boolean := false);
end entity;

architecture sim of canary_tb is
  signal clk   : std_ulogic := '0';
  signal n     : natural := 0;
  signal a, b, c, d, e, g, g2, h, i0, j : std_ulogic := '0';
  signal m     : natural := 0;
  signal never : boolean := false;
  signal q     : std_ulogic_vector(3 downto 0) := (others => '0');

  function early(x : natural) return natural is
  begin
    if x > 1000 then
      return 1; -- UNREACHED
    end if;
    if x >= 0 then
      return 2; -- REACHED
    end if;
    return 3; -- UNREACHED
  end function;

  function or_all(x : std_ulogic_vector) return std_ulogic is
    variable r : std_ulogic := '0';
  begin
    for i in x'range loop
      if x(i) = '1' then
        r := '1'; -- UNREACHED
      end if;
    end loop;
    return r; -- REACHED
  end function;

  function count_ones(x : std_ulogic_vector) return natural is
    variable r : natural := 0;
  begin
    for i in x'range loop
      if x(i) = '1' then
        r := r + 1; -- REACHED
      end if;
    end loop;
    return r; -- REACHED
  end function;

  function f1(x : natural) return natural is
  begin
    if x > 1000 then
      return 1; -- UNREACHED
    end if;
    return 0; -- REACHED
  end function;

  function f2(x : natural) return natural is
  begin
    if x < 1000 then
      return 1; -- REACHED
    end if;
    return 0; -- UNREACHED
  end function;

  procedure p1(signal s : out std_ulogic; x : in natural) is
  begin
    if x > 1000 then
      s <= '1'; -- UNREACHED
    end if;
  end procedure;

  procedure p2(signal s : out std_ulogic; x : in natural) is
  begin
    if x < 1000 then
      s <= '0'; -- REACHED
    end if;
  end procedure;

begin

  clk <= not clk after 5 ns;

  proc_a: process(clk)
  begin
    if rising_edge(clk) then
      n <= n + f1(n) + f2(n);
      p1(a, n);
      p2(a, n);
      if never then
        b <= '1'; -- UNREACHED
      end if;
    end if;
  end process;

  proc_b: process(clk)
  begin
    if rising_edge(clk) then
      case n is
        when 1000 =>
          c <= '1'; -- UNREACHED
        when others =>
          if never then
            c <= '0'; -- UNREACHED
          end if;
      end case;
    end if;
  end process;

  proc_c: process
  begin
    wait until rising_edge(clk);
    for i in 0 to 3 loop
      if never then
        d <= '0'; -- UNREACHED
      end if;
    end loop;
    if never then
      wait for 1 ns; -- UNREACHED
      d <= '1'; -- UNREACHED
    end if;
  end process;

  proc_d: process(clk)
    function local(x : natural) return natural is
    begin
      if x > 1000 then
        return 7; -- UNREACHED
      end if;
      return x; -- REACHED
    end function;
    variable v : natural;
  begin
    if rising_edge(clk) then
      v := local(n);
      e <= '1'; -- REACHED
    end if;
  end process;

  proc_f: process(clk)
    variable w : natural;
  begin
    if rising_edge(clk) then
      if n = 100000 then
        h <= '1'; -- UNREACHED
      elsif n = 200000 then
        h <= '0'; -- UNREACHED
      else
        h <= or_all("0000"); -- REACHED
      end if;
      if n > 100000 then
        i0 <= '1'; -- UNREACHED
      elsif n >= 0 then
        i0 <= '0'; -- REACHED
      end if;
      w := 0;
      while w < 3 loop
        w := w + 1; -- REACHED
        if never then
          j <= '1'; -- UNREACHED
        end if;
      end loop;
      for k in 0 to 3 loop
        next when k < 4;
        j <= '0'; -- UNREACHED
      end loop;
      for k in 0 to 3 loop
        exit when k = 0;
        j <= '1'; -- UNREACHED
      end loop;
      m <= count_ones("0101"); -- REACHED
    end if;
  end process;

  proc_g: process(clk)
    variable v : natural;
    variable u : std_ulogic;
  begin
    if rising_edge(clk) then
      if never then
        v := 1; -- UNREACHED
      else
        v := 2; -- REACHED
      end if;
      v := v + 1; -- REACHED
      if never then
        v := 3; -- UNREACHED
        v := 4; -- UNREACHED
      else
        v := 5; -- REACHED
      end if;
      u := '0'; -- REACHED
      case v is
        when 1000 =>
          v := 6; -- UNREACHED
        when 1001 =>
          v := 7; -- UNREACHED
        when others =>
          v := 8; -- REACHED
      end case;
      u := '1'; -- REACHED
      for k in 0 to 3 loop
        if never then
          exit;
        end if;
        v := k; -- REACHED
      end loop;
      u := '0'; -- REACHED
      for k in 0 to 3 loop
        if k = 0 then
          exit;
        end if;
        v := k; -- UNREACHED
      end loop;
      u := '1'; -- REACHED
      outer: for k in 0 to 1 loop
        for l in 0 to 1 loop
          next outer when l = 0;
          v := k + l; -- UNREACHED
        end loop;
        v := 9; -- UNREACHED
      end loop;
      u := '0'; -- REACHED
      v := early(n); -- REACHED
      g2 <= u; -- REACHED
    end if;
  end process;

  gen_on_g: if GEN_ON generate
    proc_e: process(clk)
    begin
      if rising_edge(clk) then
        g <= '1'; -- UNREACHED
      end if;
    end process;
  end generate;

  q(0) <= '1' when never else '0'; -- REACHED

  ender: process
  begin
    wait until n = 50;
    finish;
  end process;

end architecture;
